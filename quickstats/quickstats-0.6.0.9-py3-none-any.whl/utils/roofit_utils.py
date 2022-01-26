from typing import Union, Optional, Dict, List

import pandas as pd

import ROOT

def copy_attributes(source:"ROOT.RooAbsArg", target:"ROOT.RooAbsArg"):
    if source is target:
        return
    for attrib in source.attributes():
        target.setAttribute(attrib)
    for attrib in source.stringAttributes():
        target.setStringAttribute(attrib.first, attrib.second)
        
def get_variable_attributes(variable:ROOT.RooRealVar):
    attributes = {
        'name' : variable.GetName(),
        'value': variable.getVal(),
        'error': variable.getError(),
        'min'  : variable.getMin(),
        'max'  : variable.getMax(),
        'is_constant': variable.isConstant()
    }
    return attributes

def variable_collection_to_dataframe(var_collection:Union[list, ROOT.RooArgSet, ROOT.RooArgSet]):
    data = []
    for variable in var_collection:
        attributes = get_variable_attributes(variable)
        data.append(attributes)
    df = pd.DataFrame(data)
    return df
        
def construct_categorized_pdf_dataset(pdf:"ROOT.RooAbsPdf", dataset:"ROOT.RooDataSet", 
                               workspace:"ROOT.RooWorkspace", label:str,
                               category_name:str="adhocCat"):
    # make sure pdf is not already a simultaneous pdf
    assert pdf.ClassName() != "RooSimultaneous"
    cat = ROOT.RooCategory(category_name, category_name)
    cat.defineType(label)
    pdf_dict = {label: pdf}
    pdf_map = ExtendedModel.get_object_map(pdf_dict, "RooAbsPdf")
    dataset_dict = {label: dataset}
    dataset_map = ExtendedModel.get_object_map(data_dict, "RooDataSet")
    sim_pdf = ROOT.RooSimultaneous(pdf.GetName(), pdf.GetName(), pdf_map, cat)
    obs_and_weight = dataset.get()
    weight_var = workspace.var("weightVar")
    if not weitht_var:
        raise RuntimeError("workspace does not contain the variable `weightVar`")
    obs_and_weight.add(weight_var)
    indexed_dataset = ROOT.RooDataSet(dataset.GetName(), dataset.GetName(), obs_and_weight, 
                                      ROOT.RooFit.Index(cat),
                                      ROOT.RooFit.Import(dataset_map),
                                      ROOT.RooFit.WeightVar(weight_var))
    return sim_pdf, indexed_dataset


def factorize_pdf(observables:"ROOT.RooArgSet", pdf:"ROOT.RooAbsPdf", constraints:"ROOT.RooArgSet"):
    pdf_class = pdf.ClassName()   
    if pdf_class == "RooProdPdf":
        new_factors = ROOT.RooArgList()
        new_owned = ROOT.RooArgSet()
        pdf_list = pdf.pdfList()
        need_new = False
        for i in range(len(pdf_list)):
            pdf_i = pdf_list[i]
            new_pdf = factorize_pdf(observables, pdf_i, constraints)
            if new_pdf == 0:
                need_new = True
                continue
            if new_pdf is not pdf_i:
                need_new = True
                new_owned.add(new_pdf)
            new_factors.add(new_pdf)
        if not need_new:
            return pdf
        elif len(new_factors) == 0:
            return 0
        elif len(new_factors) == 1:
            clone_pdf = new_factors.first().Clone("{}_obsOnly".format(pdf.GetName()))
            copy_attributes(pdf, clone_pdf)
            return clone_pdf
        factorized_pdf = ROOT.RooProdPdf("{}_obsOnly".format(pdf.GetName()), "", new_factors)
        factorized_pdf.addOwnedComponents(new_owned)
        copy_attributes(pdf, factorized_pdf)
        return factorized_pdf
    elif pdf_class == "RooSimultaneous":
        cat = pdf.indexCat().Clone()
        n_bins = cat.numBins("")
        factorized_pdfs = []
        new_owned = ROOT.RooArgSet()
        need_new = False
        for i in range(n_bins):
            cat.setBin(i)
            pdf_i = pdf.getPdf(cat.getLabel())
            new_pdf = factorize_pdf(observables, pdf_i, constraints)
            factorized_pdfs.append(new_pdf)     
            if new_pdf == 0:
                raise RuntimeError("channel `{}` factorized to 0".format(cat.getLabel()))
            if new_pdf is not pdf_i:
                need_new = True
                new_owned.add(new_pdf)
                # this can be removed after version 6.28
                ROOT.SetOwnership(new_pdf, False)
        factorized_pdf = pdf
        if need_new:
            factorized_pdf = ROOT.RooSimultaneous("{}_obsOnly".format(pdf.GetName()), "", pdf.indexCat())
            for i in range(n_bins):
                cat.setBin(i)
                new_pdf = factorized_pdfs[i]
                if new_pdf:
                    factorized_pdf.addPdf(new_pdf, cat.getLabel())
            factorized_pdf.addOwnedComponents(new_owned)
        # has to delete persistent object
        cat.Delete()
        copy_attributes(pdf, factorized_pdf)
        return factorized_pdf         
    elif pdf.dependsOn(observables):
        return pdf
    else:
        if not constraints.contains(pdf):
            constraints.add(pdf)
        return 0
    
    
def rebuild_simultaneous_pdf(observables:"ROOT.RooArgSet", sim_pdf:"ROOT.RooSimultaneous"):
    assert sim_pdf.ClassName() == "RooSimultaneous"
    constraints = ROOT.RooArgList()
    cat = sim_pdf.indexCat().Clone()
    n_bins = cat.numBins("")
    factorized_pdfs = []
    new_owned = ROOT.RooArgSet()
    for i in range(n_bins):
        cat.setBin(i)
        pdf_i = sim_pdf.getPdf(cat.getLabel())
        if pdf_i == 0:
            factorized_pdfs.append(0)
            continue
        new_pdf = factorize_pdf(observables, pdf_i, constraints)     
        factorized_pdfs.append(new_pdf)
        if new_pdf == 0:
            continue
        if new_pdf is not pdf_i:
            new_owned.add(new_pdf)
            # this can be removed after version 6.28
            ROOT.SetOwnership(new_pdf, False)
    rebuilt_pdf = ROOT.RooSimultaneous("{}_reloaded".format(sim_pdf.GetName()), "", sim_pdf.indexCat())
    for i in range(n_bins):
        cat.setBin(i)
        new_pdf = factorized_pdfs[i]
        if new_pdf:
            if constraints.getSize() > 0:
                all_factors = ROOT.RooArgList(constraints)
                all_factors.add(new_pdf)
                newer_pdf = ROOT.RooProdPdf("{}_plus_constr".format(new_pdf.GetName()), "",
                                           all_factors)
                rebuilt_pdf.addPdf(newer_pdf, cat.getLabel())
                copy_attributes(new_pdf, newer_pdf)
                new_owned.add(newer_pdf)
                # this can be removed after version 6.28
                ROOT.SetOwnership(newer_pdf, False)
            else:
                rebuilt_pdf.addPdf(new_pdf, cat.getLabel())
    rebuilt_pdf.addOwnedComponents(new_owned)
    copy_attributes(sim_pdf, rebuilt_pdf)
    return rebuilt_pdf



def print_object(obj, indent=0, spacer="  ", prefix="-", show_address=False):
    if show_address:
        print(f"{spacer*indent}{prefix}{obj.GetName()}({obj.ClassName()} @ {hex(id(obj))})")
    else:
        print(f"{spacer*indent}{prefix}{obj.GetName()}({obj.ClassName()})")
        
def print_pdf_structure(pdf:"ROOT.RooAbsPdf", level:int=0, show_address=False):
    print_object(pdf, level, show_address=show_address)
    class_name = pdf.ClassName()
    if class_name == "RooSimultaneous":
        cat = pdf.indexCat().Clone()
        n_bins = cat.numBins("")
        for i in range(n_bins):
            cat.setBin(i)
            pdf_i = pdf.getPdf(cat.getLabel())
            print_pdf_structure(pdf_i, level+1, show_address=show_address)
    elif class_name == "RooProdPdf":
        pdf_list = pdf.pdfList()
        for pdf_i in pdf_list:
            print_pdf_structure(pdf_i, level+1, show_address=show_address)