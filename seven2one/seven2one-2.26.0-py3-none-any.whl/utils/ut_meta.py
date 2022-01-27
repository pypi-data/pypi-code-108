class Meta():
    def meta():
        metaString = '''
            query inventoryItems(
            $topLevelField: String!
            $topLevelType: String!
            $nestingLevel: Int! = 3
            $listNestingLevel: Int = 1
            $nestingPlusOneFields: [String!]
            $variables: [VariableValueInput!]
            ) {
            meta {
                query {
                dynamicItem(
                    topLevelField: $topLevelField
                    nestingLevel: $nestingLevel
                    listNestingLevel: $listNestingLevel
                    nestingPlusOneFields: $nestingPlusOneFields
                ) {
                    result(variables: $variables) {
                    grid {
                        columns {
                        graphQlPath
                        path
                        type {
                            name
                            isNonNullable
                        }
                        kind
                        }
                        rows {
                        values {
                            ... on StringCellValue {
                            stringValue: value
                            }
                            ... on BooleanCellValue {
                            boolValue: value
                            }
                            ... on DecimalCellValue {
                            doubleValue: value
                            }
                            ... on IntCellValue {
                            intValue: value
                            }
                            ... on DateTimeCellValue {
                            dateTimeValue: value
                            }
                        }
                        } 
                    }
                    }
                }
                } 
                typeDescription(typeName: $topLevelType) {
                ...typeDescription
                }
            }

            inventories: inventories(where: {name: {eq:  $topLevelField}}) {
                edges {
                node {
                    displayName
                    properties {
                    name  
                    __typename
                    }
                }
                }
            }
            }



            fragment typeDescription on ITypeDescription {
            ...typeDescriptionFields
            ... on ListTypeDescription {
                innerType {
                ...typeDescriptionFields
                ... on ListTypeDescription {
                    innerType {
                    ...typeDescriptionFields
                    }
                }
                ... on ObjectTypeDescription {
                    fields {
                    name
                    type {
                        ...typeDescriptionFields
                    }
                    }
                }
                ... on EnumTypeDescription {
                    ...enumFields
                }    
                }
            }
            ... on ObjectTypeDescription {
                fields {
                name
                type {
                    ...typeDescriptionFields
                    ... on ListTypeDescription {
                    innerType {
                        ...typeDescriptionFields           
                    }
                    }
                    ... on ObjectTypeDescription {
                    fields {
                        name
                        type {
                        ...typeDescriptionFields
                        }
                    }
                    } 
                    ... on EnumTypeDescription {
                    ...enumFields
                    }
                }
                }
            }
            ... on EnumTypeDescription {
                ...enumFields
            }
            }

            fragment typeDescriptionFields on ITypeDescription {
            typeKind: __typename
            name 
            isNonNullable
            }

            fragment enumFields on EnumTypeDescription {
                enumValues: values
            }

            '''
        return metaString
