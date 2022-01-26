from typing import List, Optional

from quickstats.utils.root_utils import declare_expression

ROOT_MACROS = \
{
    "TH1Utils": "namespace TH1Utils {\n"
    "    template<typename T>\n"
    "    std::vector<T> GetBinErrorArray(TH1* h, const size_t &underflow_bin=0, const size_t & overflow_bin=0)\n"
    "    {\n"
    "        const size_t n_bin = h->GetNbinsX();\n"
    "        std::vector<T> result;\n"
    "        result.reserve(n_bin);\n"
    "        const size_t bin_min = 1 - underflow_bin;\n"
    "        const size_t bin_max = n_bin + overflow_bin;\n"
    "        for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)\n"
    "            result.push_back(h->GetBinError(bin_index));\n"
    "        return result;\n"
    "    }\n"
    "    \n"
    "    template<typename T>\n"
    "    std::vector<T> GetBinCenterArray(TH1* h, const size_t &underflow_bin=0, const size_t & overflow_bin=0)\n"
    "    {\n"
    "        const size_t n_bin = h->GetNbinsX();\n"
    "        std::vector<T> result;\n"
    "        result.reserve(n_bin);\n"
    "        const size_t bin_min = 1 - underflow_bin;\n"
    "        const size_t bin_max = n_bin + overflow_bin;\n"
    "        for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)\n"
    "            result.push_back(h->GetBinCenter(bin_index));\n"
    "        return result;\n"
    "    }\n"
    "\n"
    "    template<typename T>\n"
    "    std::vector<T> GetBinContentArray(TH1* h, const size_t &underflow_bin=0, const size_t & overflow_bin=0)\n"
    "    {\n"
    "        const size_t n_bin = h->GetNbinsX();\n"
    "        std::vector<T> result;\n"
    "        result.reserve(n_bin);\n"
    "        const size_t bin_min = 1 - underflow_bin;\n"
    "        const size_t bin_max = n_bin + overflow_bin;\n"
    "        for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)\n"
    "            result.push_back(h->GetBinContent(bin_index));\n"
    "        return result;\n"
    "    }\n"
    "    \n"
    "    template<typename T>\n"
    "    std::vector<T> GetBinWidthArray(TH1* h, const size_t &underflow_bin=0, const size_t & overflow_bin=0)\n"
    "    {\n"
    "        const size_t n_bin = h->GetNbinsX();\n"
    "        std::vector<T> result;\n"
    "        result.reserve(n_bin);\n"
    "        const size_t bin_min = 1 - underflow_bin;\n"
    "        const size_t bin_max = n_bin + overflow_bin;\n"
    "        for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)\n"
    "            result.push_back(h->GetBinWidth(bin_index));\n"
    "        return result;\n"
    "    }\n"
    "    \n"
    "    template<typename T>\n"
    "    std::vector<T> GetBinLowEdgeArray(TH1* h, const size_t &underflow_bin=0, const size_t & overflow_bin=0)\n"
    "    {\n"
    "        const size_t n_bin = h->GetNbinsX();\n"
    "        std::vector<T> result;\n"
    "        result.reserve(n_bin);\n"
    "        const size_t bin_min = 1 - underflow_bin;\n"
    "        const size_t bin_max = n_bin + overflow_bin;\n"
    "        for (size_t bin_index = bin_min; bin_index <= bin_max; bin_index++)\n"
    "            result.push_back(h->GetBinLowEdge(bin_index));\n"
    "        return result;\n"
    "    }    \n"
    "};\n"
}

def load_macro(macro_name:str):
    expression = ROOT_MACROS.get(macro_name, None)
    if expression is None:
        raise ValueError(f"`{macro_name}` is not a built-in quickstats macro."
                         " Available macros are: {}".format(",".join(list(ROOT_MACROS))))
    declare_expression(expression, macro_name)

def load_macros(macro_names:Optional[List[str]]=None):
    if macro_names is None:
        macro_names = list(ROOT_MACROS)
    for macro_name in macro_names:
        load_macro(macro_name)