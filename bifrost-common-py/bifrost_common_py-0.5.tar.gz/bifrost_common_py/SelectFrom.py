"""
 * This module provides a class for decleratively selecting slices
 * from the BIFROST state. It is part of the bifrost-common suite 
 * for module developers.
 *
 * The current state version is B4 / ANVIL.
 *
 * @module SelectFrom
 * @author Ralf Mosshammer <bifrost.at@siemens.com>
 * @copyright Siemens AG Austria, 2019, 2020

 * Python implementation
 * @author Manuel Matzinger <manuel.matzinger@siemens.com>
 """

from msilib.schema import Error
from multiprocessing.dummy import Array
from ssl import CERT_REQUIRED
from bifrost_common_py.idOfRef import idOfRef
from bifrost_common_py.tokens import tkId, tkRef, tkTypeRef, tkDomain, tkParentRefs, tkChildRefs, tkDynamicRefs, tkValue, tkMemberOf
from bifrost_common_py.safepointer import safepointer
import bifrost_common_py.selectors as select

"""
 * Convenience functions to select elements from the BIFROST state.
 *
 * _SelectFrom provides a number of chainable functions to run queries against
 * a BIFROST state object. The result of each query/filter is stored in an internal
 * object, which can the be resolved towards lists of IDs or references, or more complex
 * objects representing associations.
 *
 * To use this class, employ the factory function.
 * @example
 *  allDynamicsAndStructures =
 *      SelectFrom(state)
 *      .allDynamics().and
 *      .allStructures()
 *      .asReferenceList()
 *
 *  allVoltages =
 *      SelectFrom(state)
 *      .allDynamics()
 *      .ofType('VOLTAGE-3P')
 *      .asIdList()
 *
 *  allVoltagesAndTheirAngles =
 *      SelectFrom(state)
 *      .allDynamics()
 *      .ofType('VOLTAGE-ANGLE-3P')
 *      .asIdMapOf(allVoltages)
 """
class SelectFrom:
    """
    * Create a new selection query by chaining selection functions.
    *
    * @param {object} _state - A state object as handed to the init function of a module, i.e.,
    * _including_ the directory.
    """
    def __init__(self,state):
        self.state  = state
        self.cqr    = []
        self._and   = self
        self.which  = self

    """
    * Reset the query result
    """
    def reset(self):
        self.cqr = []

    """
    * Select all dynamics and add them to the query result
    *
    * @return {object} A chainable instance of this object.
    """
    def allDynamics(self):
        self.cqr.extend(safepointer.get(self.state, select.allDynamics(), []))
        return self

    # def getDynamics(self):
    #     result = {}
    #     for ref in self.cqr:
    #         dynamics = SelectFrom.get(safepointer.get(self.state, ref), "dynamicRefs")
    #         for dynamicRef in dynamics:
    #             result[ref].append(dynamicRef)
    #     print(result)

    """
    * Select all structures from all domains and add them to the query result.
    *
    * @return {object} A chainable instance of this object.
    """
    def allStructures(self):
        allDomains = (safepointer.get(self.state, select.domains(), {})).keys()
        for domain in allDomains:
            self.cqr.extend(safepointer.get(self.state, select.allDomainElements(domain), []))
        return self

    """
    * Select all powergrid Elements (i.e. POWERGRID-CONNECTOR) and add them to the query result.
    *
    * @return {object} A chainable instance of this object.
    """
    def allPowerGridElements(self):
        self.cqr.extend(safepointer.get(self.state, select.allPowergridElements(), []))
        return self

    """
    * Select all datagrid Elements (i.e. DATAGRID-CONNECTOR) and add them to the query result.
    *
    * @return {object} A chainable instance of this object.
    """
    def allDataGridElements(self):
        self.cqr.extend(safepointer.get(self.state, select.allDatagridElements(), []))
        return self

    """
    * Select all elements with specific typeId (structures or dynamics).
    *
    * @param {string} typeId -- The type ID you search for
    *
    * @return {object} A chainable instance of this object.
    """
    def ofType(self, typeId):
        self.cqr = list(filter(lambda ref: SelectFrom.ofTypefilter(self, ref, typeId), self.cqr))
        return self

    def ofAnyType(self, typeIds):
        self.cqr = list(filter(lambda ref: SelectFrom.ofAnyTypefilter(self, ref, typeIds), self.cqr))
        return self

    """
    * Select all elements in a specific domain.
    *
    * @param {string} domain -- The domain you want to filter by
    *
    * @return {object} A chainable instance of this object.
    """
    def inDomain(self,domain):
        self.cqr = list(filter(lambda ref: SelectFrom.ofDomainfilter(self,ref,domain), self.cqr))
        return self

    def beingMemberOf(self, elementClass):
        self.cqr = list(filter(lambda ref: SelectFrom.ofMemberfilter(self,ref,elementClass), self.cqr))
        return self

    def notBeingMemberOf(self, elementClass):
        self.cqr = list(filter(lambda ref: (not SelectFrom.ofMemberfilter(self,ref,elementClass)), self.cqr))
        return self

    """
    * Select all elements with a reference to a dynamic with the specified type.
    * 
    * @param {string} typeId A dynamic type ID
    * 
    * @return {object} A chainable instance of this object.
    """
    def havingADynamic(self, typeId):
        self.cqr = list(filter(lambda ref: (not SelectFrom.ofDynamicfilter(self,ref,typeId)), self.cqr))
        return self

    """
    * Select all elements with a reference to any of the dynamics in the provided list.
    * 
    * @param {array} typeIds A list of type IDs
    * 
    * @return {object} A chainable instance of this object.
    """
    def havingAnyDynamic(self, typeIds):
        self.cqr = list(filter(lambda ref: (not SelectFrom.ofAnyDynamicfilter(self,ref,typeIds)), self.cqr))
        return self

    """
    * Select all elements which have _any_ of the typeIDs given as parameter
    * as _direct_ parents. No recursion is performed, i.e., second- or higher order
    * ancestors are _not_ taken into account.
    *
    * @param {array} parentTypeIds A list of type IDs to filter by
    *
    * @return {object} A chainable instance of this object.
    """
    def havingAParent(self,parentTypeIds):
        return self._havingAnAncestor(parentTypeIds, False)

    """
    * @see havingAParent
    """
    def havingAnyParent(self, parentTypeIds):
        return self.havingAParent(parentTypeIds)

    """
    * Select all elements which have _all_ of the typeIDs given as parameter
    * as _direct_ parents. No recursion is performed, i.e., second- or higher order
    * ancestors are _not_ taken into account.
    *
    * @param {array} parentTypeIds A list of type IDs to filter by
    *
    * @return {object} A chainable instance of this object.
    """
    def havingAllParents(self, parentTypeIds):
        self._havingAllAncestors(parentTypeIds, False)

    """
    * Select all elements which have _any_ of the typeIDs given as parameter
    * as _direct_ children. No recursion is performed, i.e., second- or higher order
    * descendants are _not_ taken into account.
    *
    * @param {array} childTypeIds A list of type IDs to filter by
    *
    * @return {object} A chainable instance of this object.
    """
    def havingAChild(self,childTypeIds):
        return self._havingAnDescendant(childTypeIds, False)

    """
    * @see havingAChild
    """
    def havingAnyChild(self, childTypeIds):
        return self.havingAChild(childTypeIds)

    """
    * Select all elements which have _all_ of the typeIDs given as parameter
    * as _direct_ children. No recursion is performed, i.e., second- or higher order
    * descendants are _not_ taken into account.
    *
    * @param {array} childTypeIds A list of type IDs to filter by
    *
    * @return {object} A chainable instance of this object.
    """
    def havingAllChildren(self, childTypeIds):
        return self._havingAllDescendants(childTypeIds, False)

    def getSpecificParent(self, specificParentId):
        return self._getSpecificParent(specificParentId, False)
    
    def getSpecificParentRef(self,specficParentId):
        result = []
        for ref in self.cqr:
            parentRefs = SelectFrom.get(safepointer.get(self.state, ref), tkParentRefs)
            for parentRef in parentRefs:
                selfparentTypeRef = SelectFrom.get(safepointer.get(self.state, parentRef), tkTypeRef)
                selfparentTypeId  = SelectFrom.get(safepointer.get(self.state, selfparentTypeRef), tkId)
                if(selfparentTypeId == specficParentId):
                        result.append(parentRef)
        self.cqr = result
        return self

    """
    * Select all elements which have _any_ of the typeIDs given as parameter
    * as ancestors of any order. If no suitable parent is found, this will
    * traverse the ancestor tree up until there are no further ancestors.
    *
    * @param {array} ancestorTypeIds A list of type IDs to filter by
    *
    * @return {object} A chainable instance of this object.
    """
    def havingAnAncestor(self,ancestorTypeIds):
        return self._havingAnAncestor(ancestorTypeIds, True)

    """
    * Select all elements which have _all_ of the typeIDs given as parameter
    * as ancestors of any order. If no suitable parent is found, this will
    * traverse the ancestor tree up until there are no further ancestors.
    *
    * @param {array} ancestorTypeIds A list of type IDs to filter by
    *
    * @return {object} A chainable instance of this object.
    """
    def havingAllAncestors(self,ancestorTypeIds):
        return self._havingAllAncestors(ancestorTypeIds, True)


    """
    * Select all elements which have _any_ of the typeIDs given as parameter
    * as descendants of any order. If no suitable child is found, this will
    * traverse the descendant tree up until there are no further descendants.
    *
    * @param {array} descendantTypeIds A list of type IDs to filter by
    *
    * @return {object} A chainable instance of this object.
    """
    def havingAnDescendant(self, descendantTypeIds):
        return self._havingAnDescendant(descendantTypeIds, False)

    """
    * Run the query you constructed so far against the state object and return a list of references.
    *
    * @return {array} -- A list of references which conform to the query.
    """
    def asReferenceList(self):
        return self.cqr
    
    """
    * Run the query you constructed so far against the state object and return a list of IDs.
    *
    * @return {array} -- A list of IDs which conform to the query.
    """
    def asIdList(self):
        refList =  self.asReferenceList()
        retList = list(map(lambda ref: SelectFrom.get(safepointer.get(self.state, ref), tkId), refList))
        return retList

    def asValueMap(self):
        result = {}
        for ref in self.cqr:
            value = SelectFrom.get(safepointer.get(self.state, ref), tkValue)
            result[ref] = value
        return result

    def asIdValueMap(self):
        result = {}
        for ref in self.cqr:
            value = SelectFrom.get(safepointer.get(self.state, ref, {}), tkValue, None)
            id    = SelectFrom.get(safepointer.get(self.state, ref, {}), tkId)
            result[id] = value
        return result

    def asReferenceMapOf(self, associateRefs):
        return self._asMapOf([*associateRefs], False)

    def asIdMapOf(self, associateRefs):
        return self._asMapOf([*associateRefs], True)

    def asIdToIdMapOf(self, associateRefs):
        return self._asMapOf([*associateRefs], True, True)

    # helper Functions
    """
    * Compare the current query result against a list of references and return a map of
    * _common ancestor associations_. This means this function, for every reference
    * in you query result and every reference in the parameter, will run up the ancestor
    * tree and see whether there are any matches between the two elements. If so, an object
    * of the shape
    *
    * {
    *  [referenceA]: [referenceB]
    * }
    *
    * is constructed, where the two references have a common ancestor.
    *
    * @param {array} associateRefs A flat array with dynamic or structure references.
    * @return {array} a list of associate map objects, as shown above.
    """
    def _asMapOf(self, associateRefs, useIds = False, useIdsInOutput=False):
        result = {}
        for ref in self.cqr:
            ancestors           = []
            currentAncestors    = []
            currentRef          = ref
            while True:
                currentAncestors = SelectFrom.get(safepointer.get(self.state, currentRef), tkParentRefs)
                ancestors.extend(currentAncestors)
                if (len(currentAncestors) > 0):
                        currentRef = currentAncestors[0]
                else:
                    break
            for associateRef in associateRefs:
                associateAncestors          = []
                currentAssociateAncestors   = []
                currentAssociateRef         = associateRef
                while True:
                        currentAssociateAncestors = SelectFrom.get(safepointer.get(self.state, currentAssociateRef, {}), tkParentRefs, [])
                        associateAncestors.extend(currentAssociateAncestors)
                        if (len(currentAssociateAncestors) > 0):
                            currentAssociateRef = currentAssociateAncestors[0]
                        else:
                            break
                a = set(ancestors)
                tmp = associateAncestors + [associateRef]
                b = set(tmp)
                i = set(filter(lambda x: x in b,a))
                if (len(i) > 0):
                    id = SelectFrom.get(safepointer.get(self.state, ref, {}), tkId)
                    associateId = SelectFrom.get(safepointer.get(self.state, associateRef,  {}), tkId)
                    key = None
                    value = None
                    if useIds:
                        key = id
                    else:
                        key = ref
                    if useIdsInOutput:
                        value = associateId
                    else:
                        value = associateRef
                    result[key] = value
                    
        return result
    
    def refHasAncestorOfType(self, ref, ancestorTypeId, recurse = True):
        parentRefs = SelectFrom.get(safepointer.get(self.state, ref), tkParentRefs)
        for parentRef in parentRefs:
            selfParentTypeRef = SelectFrom.get(safepointer.get(self.state, parentRef), tkTypeRef)
            selfParentTypeId  = SelectFrom.get(safepointer.get(self.state, selfParentTypeRef), tkId)
            if (selfParentTypeId == ancestorTypeId):
                return True
            else:
                if (recurse):
                        # check here if the current element even has parents, when not stop the recursion
                        # or else potential parentRef in the list of parentRefs could be axed
                        if(SelectFrom.get(safepointer.get(self.state, parentRef), tkParentRefs)):
                            return self.refHasAncestorOfType(parentRef, ancestorTypeId, recurse)
                # does not iterate all parentRefs in this case
                #else:
                #     return False
        return False

    def refHasDescendantOfType(self, ref, descendantTypeId, recurse = True):
        childRefs = SelectFrom.get(safepointer.get(self.state, ref), tkChildRefs)
        for childRef in childRefs:
            selfchildTypeRef = SelectFrom.get(safepointer.get(self.state, childRef), tkTypeRef)
            selfchildTypeId  = SelectFrom.get(safepointer.get(self.state, selfchildTypeRef), tkId)
            if (selfchildTypeId == descendantTypeId):
                return True
            else:
                if (recurse):
                        if(SelectFrom.get(safepointer.get(self.state, childRef), tkChildRefs)):
                            return self.refHasDescendantOfType(childRef, descendantTypeId, recurse)
        return False
    
    def refHasSpecificParentOfType(self, ref, specificParentTypeId, recurse = True):
        parentRefs = SelectFrom.get(safepointer.get(self.state, ref), tkParentRefs)
        for parentRef in parentRefs:
            selfParentTypeRef = SelectFrom.get(safepointer.get(self.state, parentRef), tkTypeRef)
            selfParentTypeId  = SelectFrom.get(safepointer.get(self.state, selfParentTypeRef), tkId)
            if (selfParentTypeId == specificParentTypeId):
                return True
        return False

    def _havingAnAncestor(self, ancestorTypeIds, recurse = True):
        self.cqr = list(filter(lambda ref: SelectFrom.havingAnAncestorfilter(self,ancestorTypeIds,recurse,ref), self.cqr))
        return self
    
    def _havingAnDescendant(self, descendantTypeIds, recurse = True):
        self.cqr = list(filter(lambda ref: SelectFrom.havingADescendantfilter(self, descendantTypeIds,recurse, ref), self.cqr))
        return self

    def _havingAllDescendants(self, descendantTypeIds, recurse = True):
        self.cqr = list(filter(lambda ref: SelectFrom.havingAllDescendantsfilter(self, descendantTypeIds,recurse, ref), self.cqr))
        return self
    
    def _getSpecificParent(self, specificParentId, recurse = True):
        self.cqr = list(filter(lambda ref: SelectFrom.specificParentfilter(self, specificParentId ,recurse, ref), self.cqr))

    def _havingAllAncestors(self, ancestorTypeIds, recurse = True):
        self.cqr = list(filter(lambda ref: SelectFrom.havingAllAncestorfilter(self,ancestorTypeIds,recurse,ref), self.cqr))
        return self
    
    def havingAnAncestorfilter(self, ancestorTypeIds, recurse, ref):
        for ancestorTypeId in ancestorTypeIds:
            if (self.refHasAncestorOfType(ref, ancestorTypeId, recurse)):
                return True
        return False
    
    def havingADescendantfilter(self, descendantTypeIds, recurse, ref):
        for descendantTypeId in descendantTypeIds:
            if (self.refHasDescendantOfType(ref, descendantTypeId, recurse)):
                return True
        return False

    def havingAllDescendantsfilter(self, descendantTypeIds, recurse, ref):
        for descendantTypeId in descendantTypeIds:
            if (not self.refHasDescendantOfType(ref,descendantTypeId, recurse)):
                return False
        return True

    def specificParentfilter(self, specificParentId,recurse,ref):
        if (self.refHasSpecificParentOfType(ref, specificParentId, recurse)):
            return True
        return False

    def havingAllAncestorfilter(self, ancestorTypeIds, recurse, ref):
        for ancestorTypeId in ancestorTypeIds:
            if (not self.refHasAncestorOfType(ref, ancestorTypeId, recurse)):
                return False 
        return True

    def ofTypefilter(self,ref,typeId):
        # potemkins give "error" but it stays stable
        typeRef       = SelectFrom.get(safepointer.get(self.state, ref), tkTypeRef)
        selfTypeId    = SelectFrom.get(safepointer.get(self.state, typeRef, {}), tkId, None)
        return selfTypeId == typeId

    def ofAnyTypefilter(self, ref, typeIds):
        typeRef       = SelectFrom.get(safepointer.get(self.state, ref), tkTypeRef)
        selfTypeId    = SelectFrom.get(safepointer.get(self.state, typeRef, {}), tkId, None)
        return selfTypeId in typeIds
        
    
    def ofDomainfilter(self,ref,domain):
        typeRef       = SelectFrom.get(safepointer.get(self.state, ref, {}), tkTypeRef)
        selfDomain    = SelectFrom.get(safepointer.get(self.state, typeRef, {}), tkDomain, None)
        return selfDomain == domain

    def ofMemberfilter(self,ref,elementclass):
        typeRef       = SelectFrom.get(safepointer.get(self.state, ref, {}), tkTypeRef)
        memberOf      = SelectFrom.get(safepointer.get(self.state, typeRef, {}), tkMemberOf, [])
        return elementclass in memberOf

    def ofDynamicfilter(self, ref, typeId):
        dynamicRefs = SelectFrom.get(safepointer.get(self.state, ref, {}), tkDynamicRefs, [])
        dynamicTypeRefs = map(lambda ref: SelectFrom.get(safepointer.get(self.state, ref, {}), tkTypeRef), dynamicRefs) 
        dynamicTypeIds = map(lambda ref: idOfRef(self.state, ref), dynamicTypeRefs)
        return typeId in dynamicTypeIds

    def ofAnyDynamicfilter(self, ref, typeIds):
        dynamicRefs = SelectFrom.get(safepointer.get(self.state, ref, {}), tkDynamicRefs, [])
        dynamicTypeRefs = map(lambda ref: SelectFrom.get(safepointer.get(self.state, ref, {}), tkTypeRef), dynamicRefs) 
        dynamicTypeIds = map(lambda ref: idOfRef(self.state, ref), dynamicTypeRefs)
        for typeId in typeIds:
            if typeId in dynamicTypeIds:
                return True
        return False

    def get(objectp, path, default = None):
        try:
            return objectp[path]
        except Exception as e:
            print(e)
            return default


class _SelectFromSubscriptionData:
    data = []
    state = {}
    cqr = []

    def __init__(self, data, state):
        self.data   = data
        self.state  = state
        self.cqr    = []

    """
    * Reset the query result
    """
    def reset(self):
        self.cqr = []

    """
    * Initialize the selection process.
    """
    def allEntries(self):
        self.cqr = self.cqr.extend(self.cqr, self.data)
        return self

    """
    * Select all entries with the specified type ID.
    * 
    * @param {String} typeId The type ID to select against
    """
    def ofType(self, typeId):
        self.cqr = list(filter(lambda ref: SelectFrom.ofTypefilter(self, ref, typeId), self.cqr))
        return self

    """
    * Select all entries with a parentRef resolving to the specified type ID.
    * 
    * @param {String} typeId The type ID of the parent to select against
    """
    def withParentOfType(self, typeId):
        if len(self.state.keys()) == 0:
            raise Exception('Selector withParentOfType(typeId) needs the state to complete. Use SelectFrom(subscriptionData, state).')
        self.cqr = list(filter(lambda ref: _SelectFromSubscriptionData.withParentFilter(self, ref, typeId), self.cqr))

        return self

    """
    * @returns {array} The query result as a raw object list (i.e., a filtered subscription data)
    """
    def asObjectList(self):
        return [self.cqr]

    """
    * @returns {array} The query result flattened to an array of values.
    """
    def asValueList(self):
        valueList = map(lambda ref: SelectFrom.get(safepointer.get(self.state, ref), tkValue), self.cqr)
        return valueList

    """
    * @returns {object} The query result as a key-value map, where the key is the dynamic reference and the value the dynamic value.
    """
    def asValueMap(self):
        result = {}
        for ref in self.cqr:
            value = SelectFrom.get(safepointer.get(self.state, ref), tkValue)
            result[ref] = value
        return result

    """
    * @returns {object} The query result as a key-value map, where the key is the dynamic ID and the value the dynamic value.
    """
    def asValueIdMap(self):
        result = {}
        for entry in self.cqr:
            ref = SelectFrom.get(safepointer.get(self.state, entry), tkId)
            value = SelectFrom.get(safepointer.get(self.state, entry), tkValue)
            result[ref] = value
        return result

    def withParentFilter(self, ref, typeId):
        parentRefs = SelectFrom.get(safepointer.get(self.state, ref), tkParentRefs)
        parentTypeRefs = map(lambda ref: SelectFrom.get(safepointer.get(self.state, ref, {}), tkTypeRef), parentRefs)
        parentTypeIds = map(lambda ref: idOfRef(self.state, ref), parentTypeRefs)
        if typeId in parentTypeIds:
            return True
        return False