#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import pytest


@pytest.fixture
def project_id():
    return "e1c7fc29ba2e612a72272324b8a842af"


@pytest.fixture
def model_id():
    return "e1c7fc29ba2e612a72272324b8a923ba"


@pytest.fixture
def cluster_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/clusterNames/".format(project_id, model_id)


@pytest.fixture
def cluster_insights_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/clusterInsights/".format(
        project_id, model_id
    )


@pytest.fixture
def job_url(project_id):
    return "https://host_name.com/projects/{}/jobs/1/".format(project_id)


# Cluster data


@pytest.fixture
def cluster_no_percent():
    return {"name": "Cluster A"}


@pytest.fixture
def cluster_with_percent():
    return {"name": "Cluster B", "percent": 13.213123}


@pytest.fixture
def clusters_data(project_id, model_id):
    return {
        "projectId": project_id,
        "modelId": model_id,
        "clusters": [
            {"name": "Cluster 1", "percent": 12.1},
            {"name": "Cluster 2", "percent": 22.2},
            {"name": "Cluster 3", "percent": 33.7},
            {"name": "Cluster 4", "percent": 32},
        ],
    }


# ClusterInsight data


@pytest.fixture
def cluster_insights_numeric_feature():
    return {
        "featureName": "some_numeric_feature",
        "featureType": "numeric",
        "insights": [
            {
                "allData": 6182554218649.518,
                "perCluster": [
                    {"statistic": 6173771480804.388, "clusterName": "Cluster 1"},
                    {"statistic": 6197859776119.403, "clusterName": "Cluster 2"},
                    {"statistic": 6174208502994.012, "clusterName": "Cluster 3"},
                    {"statistic": 6181982626931.567, "clusterName": "Cluster 4"},
                    {"statistic": 6176131085106.383, "clusterName": "Cluster 5"},
                    {"statistic": 6184868716216.216, "clusterName": "Cluster 6"},
                    {"statistic": 6195556278260.869, "clusterName": "Cluster Y"},
                ],
                "insightName": "avg",
            },
            {
                "allData": 6137927500000.0,
                "perCluster": [
                    {"statistic": 6130400000000.0, "clusterName": "Cluster 1"},
                    {"statistic": 6148752500000.0, "clusterName": "Cluster 2"},
                    {"statistic": 6129730000000.0, "clusterName": "Cluster 3"},
                    {"statistic": 6132060000000.0, "clusterName": "Cluster 4"},
                    {"statistic": 6141582500000.0, "clusterName": "Cluster 5"},
                    {"statistic": 6140957500000.0, "clusterName": "Cluster 6"},
                    {"statistic": 6150460000000.0, "clusterName": "Cluster Y"},
                ],
                "insightName": "firstQuartile",
            },
            {
                "allData": 6257230000000.0,
                "perCluster": [
                    {"statistic": 6257230000000.0, "clusterName": "Cluster 1"},
                    {"statistic": 6256460000000.0, "clusterName": "Cluster 2"},
                    {"statistic": 6256310000000.0, "clusterName": "Cluster 3"},
                    {"statistic": 6256490000000.0, "clusterName": "Cluster 4"},
                    {"statistic": 6256790000000.0, "clusterName": "Cluster 5"},
                    {"statistic": 6256750000000.0, "clusterName": "Cluster 6"},
                    {"statistic": 6257230000000.0, "clusterName": "Cluster Y"},
                ],
                "insightName": "max",
            },
            {
                "allData": 6168850000000.0,
                "perCluster": [
                    {"statistic": 6150630000000.0, "clusterName": "Cluster 1"},
                    {"statistic": 6218055000000.0, "clusterName": "Cluster 2"},
                    {"statistic": 6155730000000.0, "clusterName": "Cluster 3"},
                    {"statistic": 6166900000000.0, "clusterName": "Cluster 4"},
                    {"statistic": 6157650000000.0, "clusterName": "Cluster 5"},
                    {"statistic": 6177230000000.0, "clusterName": "Cluster 6"},
                    {"statistic": 6212220000000.0, "clusterName": "Cluster Y"},
                ],
                "insightName": "median",
            },
            {
                "allData": 6094590000000.0,
                "perCluster": [
                    {"statistic": 6094590000000.0, "clusterName": "Cluster 1"},
                    {"statistic": 6124900000000.0, "clusterName": "Cluster 2"},
                    {"statistic": 6122630000000.0, "clusterName": "Cluster 3"},
                    {"statistic": 6122710000000.0, "clusterName": "Cluster 4"},
                    {"statistic": 6121530000000.0, "clusterName": "Cluster 5"},
                    {"statistic": 6123790000000.0, "clusterName": "Cluster 6"},
                    {"statistic": 6121610000000.0, "clusterName": "Cluster Y"},
                ],
                "insightName": "min",
            },
            {
                "allData": 0.0,
                "perCluster": [
                    {"statistic": 0.0, "clusterName": "Cluster 1"},
                    {"statistic": 0.0, "clusterName": "Cluster 2"},
                    {"statistic": 0.0, "clusterName": "Cluster 3"},
                    {"statistic": 0.0, "clusterName": "Cluster 4"},
                    {"statistic": 0.0, "clusterName": "Cluster 5"},
                    {"statistic": 0.0, "clusterName": "Cluster 6"},
                    {"statistic": 0.0, "clusterName": "Cluster Y"},
                ],
                "insightName": "missingRowsPercent",
            },
            {
                "allData": 6226600000000.0,
                "perCluster": [
                    {"statistic": 6226600000000.0, "clusterName": "Cluster 1"},
                    {"statistic": 6237705000000.0, "clusterName": "Cluster 2"},
                    {"statistic": 6222020000000.0, "clusterName": "Cluster 3"},
                    {"statistic": 6224020000000.0, "clusterName": "Cluster 4"},
                    {"statistic": 6217372500000.0, "clusterName": "Cluster 5"},
                    {"statistic": 6226430000000.0, "clusterName": "Cluster 6"},
                    {"statistic": 6237930000000.0, "clusterName": "Cluster Y"},
                ],
                "insightName": "thirdQuartile",
            },
        ],
        "featureImpact": 0.30865117804983067,
    }


@pytest.fixture
def cluster_insights_categorical_feature():
    return {
        "featureName": "content",
        "featureType": "categorical",
        "insights": [
            {
                "allData": {
                    "perValueStatistics": [
                        {"categoryLevel": "beauty", "frequency": 3.022508038585209},
                        {"categoryLevel": "celebs", "frequency": 0.19292604501607716},
                        {"categoryLevel": "childrens-products", "frequency": 0.45016077170418006},
                        {"categoryLevel": "clothing", "frequency": 0.1607717041800643},
                        {"categoryLevel": "cooking", "frequency": 0.4180064308681672},
                        {"categoryLevel": "craft-ideas", "frequency": 0.19292604501607716},
                        {"categoryLevel": "entertainment", "frequency": 16.84887459807074},
                        {"categoryLevel": "fashion", "frequency": 1.157556270096463},
                        {"categoryLevel": "food-cocktails", "frequency": 0.19292604501607716},
                        {"categoryLevel": "food-recipes", "frequency": 0.2572347266881029},
                        {"categoryLevel": "health", "frequency": 0.28938906752411575},
                        {"categoryLevel": "holiday-recipes", "frequency": 0.9646302250803859},
                        {"categoryLevel": "holidays", "frequency": 3.8585209003215435},
                        {"categoryLevel": "home", "frequency": 1.2540192926045015},
                        {"categoryLevel": "home-maintenance", "frequency": 0.4180064308681672},
                        {"categoryLevel": "kitchen-tools", "frequency": 0.9646302250803859},
                        {"categoryLevel": "life", "frequency": 19.64630225080386},
                        {"categoryLevel": "pets", "frequency": 0.22508038585209003},
                        {"categoryLevel": "shopping", "frequency": 1.2540192926045015},
                        {"categoryLevel": "style-beauty", "frequency": 11.35048231511254},
                        {"categoryLevel": "www.bicycling.com", "frequency": 0.6430868167202572},
                        {"categoryLevel": "www.xyz.com", "frequency": 5.980707395498392},
                        {"categoryLevel": "www.xyz.com", "frequency": 5.691318327974277},
                        {"categoryLevel": "xyz.com", "frequency": 14.919614147909968},
                        {"categoryLevel": "www.xyz.com", "frequency": 8.745980707395498},
                    ],
                    "allOther": 0.8681672025723473,
                    "missingRowsPercent": 0.03215434083601286,
                },
                "perCluster": [
                    {
                        "perValueStatistics": [
                            {"categoryLevel": "beauty", "frequency": 2.376599634369287},
                            {"categoryLevel": "celebs", "frequency": 0.5484460694698354},
                            {
                                "categoryLevel": "cookware-reviews",
                                "frequency": 0.18281535648994515,
                            },
                            {"categoryLevel": "decorating-ideas", "frequency": 0.3656307129798903},
                            {"categoryLevel": "entertainment", "frequency": 0.7312614259597806},
                            {"categoryLevel": "fashion", "frequency": 0.9140767824497258},
                            {"categoryLevel": "health", "frequency": 0.18281535648994515},
                            {"categoryLevel": "holidays", "frequency": 4.387568555758683},
                            {"categoryLevel": "home", "frequency": 1.2797074954296161},
                            {"categoryLevel": "kitchen-tools", "frequency": 0.18281535648994515},
                            {"categoryLevel": "life", "frequency": 32.35831809872029},
                            {"categoryLevel": "organizing", "frequency": 0.18281535648994515},
                            {"categoryLevel": "pets", "frequency": 1.2797074954296161},
                            {"categoryLevel": "shopping", "frequency": 2.010968921389397},
                            {"categoryLevel": "tv", "frequency": 0.18281535648994515},
                            {
                                "categoryLevel": "www.bicycling.com",
                                "frequency": 2.1937842778793417,
                            },
                            {"categoryLevel": "www.xyz.com", "frequency": 0.18281535648994515},
                            {"categoryLevel": "www.xyz.com", "frequency": 19.926873857404022},
                            {"categoryLevel": "xyz.com", "frequency": 4.387568555758683},
                            {"categoryLevel": "www.xyz.com", "frequency": 25.95978062157221},
                        ],
                        "allOther": 0.0,
                        "missingRowsPercent": 0.18281535648994515,
                        "clusterName": "Cluster 1",
                    },
                    {
                        "perValueStatistics": [
                            {"categoryLevel": "entertainment", "frequency": 86.56716417910448},
                            {"categoryLevel": "www.xyz.com", "frequency": 13.432835820895523},
                        ],
                        "allOther": 0.0,
                        "missingRowsPercent": 0.0,
                        "clusterName": "Cluster 2",
                    },
                    {
                        "perValueStatistics": [
                            {
                                "categoryLevel": "childrens-products",
                                "frequency": 1.596806387225549,
                            },
                            {"categoryLevel": "entertainment", "frequency": 0.1996007984031936},
                            {"categoryLevel": "hair", "frequency": 0.1996007984031936},
                            {"categoryLevel": "holidays", "frequency": 0.3992015968063872},
                            {"categoryLevel": "life", "frequency": 81.0379241516966},
                            {"categoryLevel": "shopping", "frequency": 0.1996007984031936},
                            {
                                "categoryLevel": "www.bicycling.com",
                                "frequency": 0.3992015968063872,
                            },
                            {"categoryLevel": "www.xyz.com", "frequency": 0.7984031936127745},
                            {"categoryLevel": "www.xyz.com", "frequency": 5.189620758483034},
                            {"categoryLevel": "www.xyz.com", "frequency": 9.980039920159681},
                        ],
                        "allOther": 0.0,
                        "missingRowsPercent": 0.0,
                        "clusterName": "Cluster 3",
                    },
                    {
                        "perValueStatistics": [
                            {"categoryLevel": "beauty", "frequency": 12.582781456953642},
                            {"categoryLevel": "entertainment", "frequency": 0.22075055187637968},
                            {"categoryLevel": "fashion", "frequency": 6.622516556291391},
                            {"categoryLevel": "style-beauty", "frequency": 76.82119205298014},
                            {"categoryLevel": "www.xyz.com", "frequency": 3.752759381898455},
                        ],
                        "allOther": 0.0,
                        "missingRowsPercent": 0.0,
                        "clusterName": "Cluster 4",
                    },
                    {
                        "perValueStatistics": [
                            {"categoryLevel": "cooking", "frequency": 0.6382978723404256},
                            {"categoryLevel": "food-cocktails", "frequency": 1.2765957446808511},
                            {"categoryLevel": "food-news", "frequency": 0.6382978723404256},
                            {"categoryLevel": "food-recipes", "frequency": 1.4893617021276595},
                            {"categoryLevel": "holiday-recipes", "frequency": 2.5531914893617023},
                            {"categoryLevel": "kitchen-tools", "frequency": 2.127659574468085},
                            {"categoryLevel": "www.bicycling.com", "frequency": 0.425531914893617},
                            {"categoryLevel": "www.xyz.com", "frequency": 3.1914893617021276},
                            {"categoryLevel": "xyz.com", "frequency": 87.65957446808511},
                        ],
                        "allOther": 0.0,
                        "missingRowsPercent": 0.0,
                        "clusterName": "Cluster 5",
                    },
                    {
                        "perValueStatistics": [
                            {"categoryLevel": "celebs", "frequency": 1.0135135135135136},
                            {"categoryLevel": "entertainment", "frequency": 93.91891891891892},
                            {"categoryLevel": "www.xyz.com", "frequency": 5.0675675675675675},
                        ],
                        "allOther": 0.0,
                        "missingRowsPercent": 0.0,
                        "clusterName": "Cluster 6",
                    },
                    {
                        "perValueStatistics": [
                            {"categoryLevel": "beauty", "frequency": 4.173913043478261},
                            {
                                "categoryLevel": "childrens-products",
                                "frequency": 1.0434782608695652,
                            },
                            {"categoryLevel": "clothing", "frequency": 0.8695652173913043},
                            {"categoryLevel": "cooking", "frequency": 1.7391304347826086},
                            {"categoryLevel": "craft-ideas", "frequency": 1.0434782608695652},
                            {
                                "categoryLevel": "decorating-ideas",
                                "frequency": 0.34782608695652173,
                            },
                            {"categoryLevel": "entertainment", "frequency": 1.391304347826087},
                            {"categoryLevel": "gardening", "frequency": 0.5217391304347826},
                            {"categoryLevel": "health", "frequency": 1.391304347826087},
                            {"categoryLevel": "holiday-recipes", "frequency": 3.130434782608696},
                            {"categoryLevel": "holidays", "frequency": 16.347826086956523},
                            {"categoryLevel": "home", "frequency": 5.565217391304348},
                            {"categoryLevel": "home-design", "frequency": 0.5217391304347826},
                            {"categoryLevel": "home-maintenance", "frequency": 2.260869565217391},
                            {"categoryLevel": "home-products", "frequency": 0.6956521739130435},
                            {"categoryLevel": "kitchen-tools", "frequency": 3.3043478260869565},
                            {"categoryLevel": "life", "frequency": 4.869565217391305},
                            {"categoryLevel": "organizing", "frequency": 0.34782608695652173},
                            {"categoryLevel": "shopping", "frequency": 4.695652173913044},
                            {"categoryLevel": "style-beauty", "frequency": 0.8695652173913043},
                            {
                                "categoryLevel": "www.bicycling.com",
                                "frequency": 0.6956521739130435,
                            },
                            {"categoryLevel": "www.xyz.com", "frequency": 19.652173913043477},
                            {"categoryLevel": "www.xyz.com", "frequency": 4.695652173913044},
                            {"categoryLevel": "xyz.com", "frequency": 4.869565217391305},
                            {"categoryLevel": "www.xyz.com", "frequency": 13.91304347826087},
                        ],
                        "allOther": 1.0434782608695652,
                        "missingRowsPercent": 0.0,
                        "clusterName": "Cluster Y",
                    },
                ],
                "insightName": "categoryLevelFrequencyPercent",
            }
        ],
        "featureImpact": 0.847975860293234,
    }


@pytest.fixture
def cluster_insights_image_feature():
    return {
        "featureName": "social_image_url",
        "featureType": "image",
        "insights": [
            {
                "allData": {
                    "imageEntities": [
                        "61795a3736f55ef3c38529cc",
                        "61795a5e36f55ef3c38529fe",
                        "61795a3736f55ef3c38529cd",
                        "61795a3736f55ef3c38529f6",
                        "61795a5e36f55ef3c38529ff",
                        "61795a5e36f55ef3c3852a00",
                        "61795a3736f55ef3c38529bc",
                        "61795a5e36f55ef3c3852a01",
                        "61795a3736f55ef3c38529fb",
                        "61795a5e36f55ef3c3852a02",
                    ],
                    "percentageOfMissingImages": 1.0932475884244373,
                },
                "perCluster": [
                    {
                        "images": [
                            "61795a3736f55ef3c38529b8",
                            "61795a3736f55ef3c38529b9",
                            "61795a3736f55ef3c38529ba",
                            "61795a3736f55ef3c38529bb",
                            "61795a3736f55ef3c38529bc",
                            "61795a3736f55ef3c38529bd",
                            "61795a3736f55ef3c38529be",
                            "61795a3736f55ef3c38529bf",
                            "61795a3736f55ef3c38529c0",
                            "61795a3736f55ef3c38529c1",
                        ],
                        "percentageOfMissingImages": 4.570383912248629,
                        "clusterName": "Cluster 1",
                    },
                    {
                        "images": [
                            "61795a3736f55ef3c38529c2",
                            "61795a3736f55ef3c38529c3",
                            "61795a3736f55ef3c38529c4",
                            "61795a3736f55ef3c38529c5",
                            "61795a3736f55ef3c38529c6",
                            "61795a3736f55ef3c38529c7",
                            "61795a3736f55ef3c38529c8",
                            "61795a3736f55ef3c38529c9",
                            "61795a3736f55ef3c38529ca",
                            "61795a3736f55ef3c38529cb",
                        ],
                        "percentageOfMissingImages": 1.1194029850746268,
                        "clusterName": "Cluster 2",
                    },
                    {
                        "images": [
                            "61795a3736f55ef3c38529cc",
                            "61795a3736f55ef3c38529cd",
                            "61795a3736f55ef3c38529ce",
                            "61795a3736f55ef3c38529cf",
                            "61795a3736f55ef3c38529d0",
                            "61795a3736f55ef3c38529d1",
                            "61795a3736f55ef3c38529d2",
                            "61795a3736f55ef3c38529d3",
                            "61795a3736f55ef3c38529d4",
                            "61795a3736f55ef3c38529d5",
                        ],
                        "percentageOfMissingImages": 0.0,
                        "clusterName": "Cluster 3",
                    },
                    {
                        "images": [
                            "61795a3736f55ef3c38529d6",
                            "61795a3736f55ef3c38529d7",
                            "61795a3736f55ef3c38529d8",
                            "61795a3736f55ef3c38529d9",
                            "61795a3736f55ef3c38529da",
                            "61795a3736f55ef3c38529db",
                            "61795a3736f55ef3c38529dc",
                            "61795a3736f55ef3c38529dd",
                            "61795a3736f55ef3c38529de",
                            "61795a3736f55ef3c38529df",
                        ],
                        "percentageOfMissingImages": 0.6622516556291391,
                        "clusterName": "Cluster 4",
                    },
                    {
                        "images": [
                            "61795a3736f55ef3c38529e0",
                            "61795a3736f55ef3c38529e1",
                            "61795a3736f55ef3c38529e2",
                            "61795a3736f55ef3c38529e3",
                            "61795a3736f55ef3c38529e4",
                            "61795a3736f55ef3c38529e5",
                            "61795a3736f55ef3c38529e6",
                            "61795a3736f55ef3c38529e7",
                            "61795a3736f55ef3c38529e8",
                            "61795a3736f55ef3c38529e9",
                        ],
                        "percentageOfMissingImages": 0.2127659574468085,
                        "clusterName": "Cluster 5",
                    },
                    {
                        "images": [
                            "61795a3736f55ef3c38529ea",
                            "61795a3736f55ef3c38529eb",
                            "61795a3736f55ef3c38529ec",
                            "61795a3736f55ef3c38529ed",
                            "61795a3736f55ef3c38529ee",
                            "61795a3736f55ef3c38529ef",
                            "61795a3736f55ef3c38529f0",
                            "61795a3736f55ef3c38529f1",
                            "61795a3736f55ef3c38529f2",
                            "61795a3736f55ef3c38529f3",
                        ],
                        "percentageOfMissingImages": 0.6756756756756757,
                        "clusterName": "Cluster 6",
                    },
                    {
                        "images": [
                            "61795a3736f55ef3c38529f4",
                            "61795a3736f55ef3c38529f5",
                            "61795a3736f55ef3c38529f6",
                            "61795a3736f55ef3c38529f7",
                            "61795a3736f55ef3c38529f8",
                            "61795a3736f55ef3c38529f9",
                            "61795a3736f55ef3c38529fa",
                            "61795a3736f55ef3c38529fb",
                            "61795a3736f55ef3c38529fc",
                            "61795a3736f55ef3c38529fd",
                        ],
                        "percentageOfMissingImages": 0.0,
                        "clusterName": "Cluster Y",
                    },
                ],
                "insightName": "representativeImages",
            }
        ],
        "featureImpact": 1.0,
    }


@pytest.fixture
def cluster_insights_text_feature():
    return {
        "featureName": "url",
        "featureType": "text",
        "insights": [
            {
                "allData": {
                    "perValueStatistics": [
                        {
                            "ngram": "https",
                            "importance": 1.0,
                            "contextualExtracts": [
                                "https://www.xyz.com/some/url-1",
                                "https://www.xyz.com/some/url-2",
                                "https://www.xyz.com/some/url-3",
                            ],
                        },
                        {
                            "ngram": "com",
                            "importance": 1.0,
                            "contextualExtracts": [
                                "https://www.xyz.com/beauty/",
                                "https://www.xyz.com/style-beauty/",
                                "https://www.xyz.com/style/",
                            ],
                        },
                        {
                            "ngram": "www",
                            "importance": 1.0,
                            "contextualExtracts": [
                                "https://www.xyz.com/style-beauty/beauty/advice/",
                                "https://www.xyz.com/style-beauty/fashion/",
                                "https://www.xyz.com/diy-crafts/",
                                "https://www.xyz.com/life/entertainment/",
                            ],
                        },
                        {
                            "ngram": "cosmopolitan",
                            "importance": 0.35659163987138265,
                            "contextualExtracts": [
                                "https://www.xyz.com/entertainment/celebs/",
                                "https://www.xyz.com/entertainment/movies/",
                                "https://www.xyz.com/lifestyle/most-expensive",
                            ],
                        },
                        {
                            "ngram": "goodhousekeeping",
                            "importance": 0.33762057877813506,
                            "contextualExtracts": [
                                "https://www.xyz.com/beauty/fashion/",
                                "https://www.xyz.com/beauty/",
                                "https://www.xyz.com/clothing/",
                            ],
                        },
                        {
                            "ngram": "entertainment",
                            "importance": 0.3260450160771704,
                            "contextualExtracts": [
                                "https://www.xyz.com/entertainment/celebs/",
                                "https://www.xyz.com/entertainment/",
                                "https://www.xyz.com/life/entertainment/",
                            ],
                        },
                        {
                            "ngram": "life",
                            "importance": 0.29710610932475884,
                            "contextualExtracts": [
                                "https://www.xyz.com/life/entertainment/",
                                "https://www.xyz.com/life/120-years-of-style",
                                "https://www.xyz.com/life/news/",
                            ],
                        },
                        {
                            "ngram": "beauty",
                            "importance": 0.1742765273311897,
                            "contextualExtracts": [
                                "https://www.xyz.com/style-beauty/beauty/advice/",
                                "https://www.xyz.com/style-beauty/fashion/",
                                "https://www.xyz.com/style-beauty/fashion//top-gifts",
                            ],
                        },
                        {
                            "ngram": "delish",
                            "importance": 0.1742765273311897,
                            "contextualExtracts": [
                                "https://www.xyz.com/food-delish/",
                                "https://www.xyz.com/food/delish",
                            ],
                        },
                        {
                            "ngram": "style",
                            "importance": 0.142443729903537,
                            "contextualExtracts": [
                                "https://www.xyz.com/style-beauty/beauty/advice/",
                                "https://www.xyz.com/life/120-years-of-style",
                                "www.xyz.com/entertainment/celebs/style-photos",
                            ],
                        },
                    ],
                    "missingRowsPercent": 0.0,
                },
                "perCluster": [
                    {
                        "perValueStatistics": [
                            {
                                "ngram": "legends",
                                "importance": 590.3802559414991,
                                "contextualExtracts": [
                                    "abc.com/holidays/christmas-ideas/legends",
                                    "w.abc.com/life/entertainment/g29714568/photos-legends",
                                ],
                            },
                            {
                                "ngram": "lucille",
                                "importance": 449.8135283363802,
                                "contextualExtracts": [
                                    "https://www.xyz.com/life/g3460/lucille",
                                    "https://www.xyz.com/beauty/g3608/lucille",
                                ],
                            },
                            {
                                "ngram": "amazing",
                                "importance": 449.8135283363802,
                                "contextualExtracts": [
                                    "https://www.xyz.com/rides/g24516152/amazing",
                                    "https://www.xyz.com/life/news/g4479/amazing-wedding",
                                    "https://www.xyz.com/life/relationships/g4389/amazing",
                                ],
                            },
                            {
                                "ngram": "ball",
                                "importance": 449.8135283363802,
                                "contextualExtracts": [
                                    "https://www.xyz.com/life/ball-vintage-photos",
                                    "https://www.xyz.com/beauty/lucille-photos",
                                    "https://www.xyz.com/life/entertainment/lucille-set",
                                ],
                            },
                            {
                                "ngram": "parenting",
                                "importance": 407.64351005484457,
                                "contextualExtracts": [
                                    "https://www.xyz.com/life/parenting/",
                                    "https://www.xyz.com/life/parenting/mother-daughter",
                                    "https://www.xyz.com/life/parenting/summer-camp",
                                ],
                            },
                            {
                                "ngram": "1970s",
                                "importance": 365.4734917733089,
                                "contextualExtracts": [
                                    "https://www.xyz.com/life/1970s/celebrity",
                                    "https://www.xyz.com/life/1970s/iconic",
                                    "https://www.xyz.com/life/1970s/party",
                                ],
                            },
                            {
                                "ngram": "retro",
                                "importance": 337.3601462522851,
                                "contextualExtracts": [
                                    "https://www.xyz.com/life/news/g4479/amazing-retro",
                                    "https://www.xyz.com/life/relationships/g4389/retro",
                                ],
                            },
                            {
                                "ngram": "g29232102",
                                "importance": 337.3601462522851,
                                "contextualExtracts": [
                                    "https://www.xyz.com/life/entertainment/g29232102/"
                                ],
                            },
                            {
                                "ngram": "g5115",
                                "importance": 281.1334552102376,
                                "contextualExtracts": ["https://www.xyz.com/life/g5115/"],
                            },
                            {
                                "ngram": "around",
                                "importance": 253.02010968921385,
                                "contextualExtracts": [
                                    "https://www.xyz.com/life/iconic-stores-no-longer-around",
                                    "https://www.xyz.com/life/g25135266/no-longer-around",
                                    "https://www.xyz.com/life/around/g28035638/",
                                ],
                            },
                        ],
                        "missingRowsPercent": 0.0,
                        "clusterName": "Cluster 1",
                    },
                    {
                        "perValueStatistics": [
                            {
                                "ngram": "bachelorette",
                                "importance": 2481.44776119403,
                                "contextualExtracts": [
                                    "https://www.xyz.com/entertainment/tv/bachelorette-celeb",
                                    "s://www.xyz.com/entertainment/tv/bachelorette-moments",
                                    "www.xyz.com/entertainment/tv/funniest-bachelorette",
                                ],
                            },
                            {
                                "ngram": "bachelor",
                                "importance": 2322.3805970149256,
                                "contextualExtracts": [
                                    "https://www.xyz.com/entertainment/tv/a22862445/bachelor",
                                    "https://www.xyz.com/entertainment/tv/the-bachelor",
                                    "https://www.xyz.com/entertainment/tv/worst-bachelor",
                                ],
                            },
                            {
                                "ngram": "paradise",
                                "importance": 954.4029850746269,
                                "contextualExtracts": [
                                    "https://www.xyz.com/entertainment/tv/paradise",
                                    "https://www.xyz.com/entertainment/tv/bachelor-in-paradise",
                                    "https://www.xyz.com/entertainment/tv/paradise-scenes",
                                ],
                            },
                            {
                                "ngram": "g30851505",
                                "importance": 954.4029850746269,
                                "contextualExtracts": [
                                    "https://www.xyz.com/entertainment/tv/g30851505/bachelor"
                                ],
                            },
                            {
                                "ngram": "16",
                                "importance": 763.5223880597015,
                                "contextualExtracts": [
                                    "https://www.xyz.com/entertainment/tv/my-super-sweet-16",
                                    "https://www.xyz.com/entertainment/tv/craziest-16",
                                ],
                            },
                            {
                                "ngram": "wildest",
                                "importance": 763.5223880597015,
                                "contextualExtracts": [
                                    "https://www.xyz.com/entertainment/tv/g33333559/wildest",
                                    "https://www.xyz.com/entertainment/tv/g35831222/wildest",
                                ],
                            },
                            {
                                "ngram": "g22200176",
                                "importance": 636.2686567164179,
                                "contextualExtracts": [
                                    "https://www.xyz.com/entertainment/tv/g22200176"
                                ],
                            },
                            {
                                "ngram": "g29822777",
                                "importance": 572.6417910447761,
                                "contextualExtracts": [
                                    "https://www.xyz.com/entertainment/tv/g29822777/actors"
                                ],
                            },
                            {
                                "ngram": "g35990566",
                                "importance": 445.3880597014925,
                                "contextualExtracts": [
                                    "https://www.xyz.com/entertainment/g35990566/best"
                                ],
                            },
                            {
                                "ngram": "lead",
                                "importance": 445.3880597014925,
                                "contextualExtracts": [
                                    "https://www.xyz.com/entertainment/tv/g33951053/bachelor"
                                ],
                            },
                        ],
                        "missingRowsPercent": 0.0,
                        "clusterName": "Cluster 2",
                    },
                    {
                        "perValueStatistics": [
                            {
                                "ngram": "they",
                                "importance": 406.19161676646706,
                                "contextualExtracts": [
                                    "//www.xyz.com/life/entertainment/g3889/how-look-they-now",
                                    "xyz.com/life/entertainment/a33482673/are-they-now",
                                    "https://www.xyz.com/life/entertainment/g2517/they-now",
                                    "ps://www.xyz.com/life/entertainment/g3768/are-they-now",
                                ],
                            },
                            {
                                "ngram": "eggs",
                                "importance": 374.94610778443115,
                                "contextualExtracts": [
                                    "https://www.xyz.com/life/easter-eggs",
                                    "https://www.xyz.com/life/entertainment/easter-eggs",
                                ],
                            },
                            {
                                "ngram": "true",
                                "importance": 343.70059880239523,
                                "contextualExtracts": [
                                    "https://www.xyz.com/life/true-story",
                                    "https://www.xyz.com/life/entertainment/best-true",
                                    "https://www.xyz.com/life/entertainment/true-story",
                                ],
                            },
                            {
                                "ngram": "somename",
                                "importance": 281.20958083832335,
                                "contextualExtracts": [
                                    "https://www.xyz.com/one/entertainment/somename-easter-eggs"
                                ],
                            },
                            {
                                "ngram": "g27455032",
                                "importance": 281.20958083832335,
                                "contextualExtracts": [
                                    "https://www.xyz.com/one/entertainment/g27455032/eggs"
                                ],
                            },
                            {
                                "ngram": "hamilton",
                                "importance": 281.20958083832335,
                                "contextualExtracts": [
                                    "https://www.xyz.com/life/entertainment/hamilton-quotes",
                                    "https://www.xyz.com/life/entertainment/hamilton-original",
                                ],
                            },
                            {
                                "ngram": "g3775",
                                "importance": 281.20958083832335,
                                "contextualExtracts": [
                                    "https://www.xyz.com/life/entertainment/g3775/years"
                                ],
                            },
                            {
                                "ngram": "g34810559",
                                "importance": 281.20958083832335,
                                "contextualExtracts": [
                                    "https://www.xyz.com/life/entertainment/g34810559/great"
                                ],
                            },
                            {
                                "ngram": "g5022",
                                "importance": 249.9640718562874,
                                "contextualExtracts": [
                                    "https://www.xyz.com/life/news/g5022/white-house"
                                ],
                            },
                            {
                                "ngram": "snl",
                                "importance": 249.9640718562874,
                                "contextualExtracts": [
                                    "https://www.xyz.com/life/entertainment/g30823804/snl",
                                    "https://www.xyz.com/life/entertainment/g32239917/snl-cast",
                                    "https://www.xyz.com/life/entertainment/g35736/famous-snl",
                                ],
                            },
                        ],
                        "missingRowsPercent": 0.0,
                        "clusterName": "Cluster 3",
                    },
                    {
                        "perValueStatistics": [
                            {
                                "ngram": "miss",
                                "importance": 703.841059602649,
                                "contextualExtracts": [
                                    "https://www.xyz.com/style-beauty/fashion/miss",
                                    "https://www.xyz.com/style-beauty/miss",
                                    "https://www.xyz.com/beauty/miss",
                                ],
                            },
                            {
                                "ngram": "meet",
                                "importance": 527.8807947019867,
                                "contextualExtracts": [
                                    "https://www.xyz.com/style-beauty/news/g5532/meet",
                                    "https://www.xyz.com/beauty/fashion/g3369/celeb-meet",
                                ],
                            },
                            {
                                "ngram": "wore",
                                "importance": 527.8807947019867,
                                "contextualExtracts": [
                                    "https://www.xyz.com/style-beauty/news/g5532/celeb-wore",
                                    "https://www.xyz.com/beauty/fashion/g3369/wore-to-meet",
                                ],
                            },
                            {
                                "ngram": "gowns",
                                "importance": 510.28476821192044,
                                "contextualExtracts": [
                                    "https://www.xyz.com/style-beauty/fashion/gowns",
                                    "https://www.xyz.com/style-beauty/gowns",
                                ],
                            },
                            {
                                "ngram": "g29700272",
                                "importance": 492.6887417218543,
                                "contextualExtracts": [
                                    "https://www.xyz.com/style-beauty/beauty/g29700272/abc"
                                ],
                            },
                            {
                                "ngram": "shoe",
                                "importance": 492.6887417218543,
                                "contextualExtracts": [
                                    "https://www.xyz.com/style-beauty/fashion/g14416869/shoe",
                                    "https://www.xyz.com/style-beauty/fashion/g5911/shoe-1",
                                ],
                            },
                            {
                                "ngram": "tricks",
                                "importance": 492.6887417218543,
                                "contextualExtracts": [
                                    "osmxyz.com/style-beauty/fashion/g24440615/tricks",
                                    "osmxyz.com/style-beauty/fashion/g29740386/tricks-1",
                                ],
                            },
                            {
                                "ngram": "breakup",
                                "importance": 492.6887417218543,
                                "contextualExtracts": [
                                    "https://www.xyz.com/style-beauty/beauty/breakup"
                                ],
                            },
                            {
                                "ngram": "haircuts",
                                "importance": 492.6887417218543,
                                "contextualExtracts": [
                                    "https://www.xyz.com/style-beauty/beauty/breakup"
                                ],
                            },
                            {
                                "ngram": "evening",
                                "importance": 457.4966887417218,
                                "contextualExtracts": [
                                    "www.xyz.com/style-beauty/fashion/evening",
                                    "www.xyz.com/style-beauty/fashion/evening-gowns",
                                ],
                            },
                        ],
                        "missingRowsPercent": 0.0,
                        "clusterName": "Cluster 4",
                    },
                    {
                        "perValueStatistics": [
                            {
                                "ngram": "g3336",
                                "importance": 404.4255319148936,
                                "contextualExtracts": ["https://xyz.com/food-news/g3336/what"],
                            },
                            {
                                "ngram": "g3366",
                                "importance": 404.4255319148936,
                                "contextualExtracts": [
                                    "https://xyz.com/food/g3366/celebrity-eating-habits"
                                ],
                            },
                            {
                                "ngram": "flavors",
                                "importance": 370.7234042553191,
                                "contextualExtracts": [
                                    "https://xyz.com/food-news/drinks-flavors",
                                    "https://xyz.com/food-news/best-pringle-flavors",
                                ],
                            },
                            {
                                "ngram": "g4759",
                                "importance": 370.7234042553191,
                                "contextualExtracts": ["https://xyz.com/food/g4759/outdated"],
                            },
                            {
                                "ngram": "restaurants",
                                "importance": 318.6382978723404,
                                "contextualExtracts": [
                                    "https://xyz.com/food-news/restaurants",
                                    "https://xyz.com/restaurants",
                                    "https://xyz.com/restaurants/g19577116",
                                ],
                            },
                            {
                                "ngram": "cakes",
                                "importance": 303.3191489361702,
                                "contextualExtracts": [
                                    "https://www.xyz.com/food-drinks/g4716/thanksgiving-cakes",
                                    "https://xyz.com/cooking/g2086/layer-cakes",
                                ],
                            },
                            {
                                "ngram": "g20703488",
                                "importance": 269.6170212765957,
                                "contextualExtracts": [
                                    "https://xyz.com/food-news/g20703488/trader"
                                ],
                            },
                            {
                                "ngram": "ice",
                                "importance": 269.6170212765957,
                                "contextualExtracts": [
                                    "https://xyz.com/food-news/g3503/most-popular-ice",
                                    "https://xyz.com/food/g2795/50-states-crazy-ice",
                                ],
                            },
                            {
                                "ngram": "network",
                                "importance": 269.6170212765957,
                                "contextualExtracts": [
                                    "https://xyz.com/food/g3844/cancelled-food-network",
                                    "https://xyz.com/food/g4838/best-food-network-shows-ever",
                                    "https://xyz.com/restaurants/g4114/where-are-these-food",
                                ],
                            },
                            {
                                "ngram": "g4420",
                                "importance": 269.6170212765957,
                                "contextualExtracts": ["https://xyz.com/food/g4420/strict-rules"],
                            },
                        ],
                        "missingRowsPercent": 0.0,
                        "clusterName": "Cluster 5",
                    },
                    {
                        "perValueStatistics": [
                            {
                                "ngram": "celebs",
                                "importance": 1654.1756756756758,
                                "contextualExtracts": [
                                    "https://www.xyz.com/entertainment/celebs/",
                                    "https://www.xyz.com/entertainment/celebs/123",
                                ],
                            },
                            {
                                "ngram": "g29438393",
                                "importance": 855.6081081081081,
                                "contextualExtracts": [
                                    "https://www.xyz.com/entertainment/celebs/g29438393"
                                ],
                            },
                            {
                                "ngram": "g31178585",
                                "importance": 627.4459459459459,
                                "contextualExtracts": [
                                    "https://www.xyz.com/entertainment/celebs/g31178585"
                                ],
                            },
                            {
                                "ngram": "look1",
                                "importance": 570.4054054054054,
                                "contextualExtracts": [
                                    "https://www.xyz.com/entertainment/celebs/look1"
                                ],
                            },
                            {
                                "ngram": "g30915146",
                                "importance": 570.4054054054054,
                                "contextualExtracts": ["https://www.xyz.com/g30915146"],
                            },
                            {
                                "ngram": "divorce",
                                "importance": 513.3648648648649,
                                "contextualExtracts": [
                                    "//www.xyz.com/entertainment/divorce",
                                    "cosmxyz.com/entertainment/celebs/divorce",
                                    "ww.cosmxyz.com/entertainment/celebs/divorce",
                                ],
                            },
                            {
                                "ngram": "same",
                                "importance": 456.3243243243243,
                                "contextualExtracts": ["osmxyz.com/entertainment/news/g5678/same"],
                            },
                            {
                                "ngram": "g5678",
                                "importance": 456.3243243243243,
                                "contextualExtracts": [
                                    "https://www.xyz.com/entertainment/news/g5678/"
                                ],
                            },
                            {
                                "ngram": "boyfriends",
                                "importance": 456.3243243243243,
                                "contextualExtracts": [
                                    "/www.xyz.com/entertainment/celebs/boyfriends",
                                    "mxyz.com/entertainment/celebs/a28645297/boyfriends",
                                    "ttps://www.xyz.com/entertainment/celebs/boyfriends",
                                ],
                            },
                            {
                                "ngram": "daughters",
                                "importance": 456.3243243243243,
                                "contextualExtracts": [
                                    "https://www.xyz.com/entertainment/news/daughters"
                                ],
                            },
                        ],
                        "missingRowsPercent": 0.0,
                        "clusterName": "Cluster 6",
                    },
                    {
                        "perValueStatistics": [
                            {
                                "ngram": "organization",
                                "importance": 370.3304347826087,
                                "contextualExtracts": [
                                    "https://www.xyz.com/home-maintenance/organization",
                                    "https://www.xyz.com/home-maintenance/organization/g2505/",
                                ],
                            },
                            {
                                "ngram": "maintenance",
                                "importance": 343.8782608695652,
                                "contextualExtracts": [
                                    "https://www.xyz.com/home-maintenance/organization",
                                    "https://www.xyz.com/home-maintenance/organization/best",
                                    "https://www.xyz.com/home-maintenance/",
                                ],
                            },
                            {
                                "ngram": "worth",
                                "importance": 343.8782608695652,
                                "contextualExtracts": [
                                    "://www.xyz.com/shopping/antiques/worth",
                                    "https://www.xyz.com/home/is-it-worth",
                                    "ttps://www.xyz.com/life/entertainment/net-worth",
                                ],
                            },
                            {
                                "ngram": "g2610",
                                "importance": 343.8782608695652,
                                "contextualExtracts": ["https://www.xyz.com/home/tips/g2610"],
                            },
                            {
                                "ngram": "design",
                                "importance": 290.97391304347826,
                                "contextualExtracts": [
                                    "https://www.xyz.com/lifestyle/design",
                                    "https://www.xyz.com/home-design/design",
                                    "https://www.xyz.com/home-design/decorating-ideas/design",
                                ],
                            },
                            {
                                "ngram": "g2750",
                                "importance": 264.5217391304348,
                                "contextualExtracts": ["https://www.xyz.com/holidays/g2750"],
                            },
                            {
                                "ngram": "craft",
                                "importance": 264.5217391304348,
                                "contextualExtracts": [
                                    "https://www.xyz.com/diy-crafts/craft",
                                    "https://www.xyz.com/home/craft-ideas/craft",
                                    "https://www.xyz.com/home/craft-ideas/g4281/craft",
                                ],
                            },
                            {
                                "ngram": "organizing",
                                "importance": 251.29565217391303,
                                "contextualExtracts": [
                                    "https://www.xyz.com/home-maintenance/organization",
                                    "https://www.xyz.com/home/organizing/g4785",
                                    "https://www.xyz.com/home/organizing/tips/g111",
                                ],
                            },
                            {
                                "ngram": "antique",
                                "importance": 238.06956521739133,
                                "contextualExtracts": [
                                    "https://www.xyz.com/shopping/antiques",
                                    "https://www.xyz.com/home/g35180502/antique",
                                ],
                            },
                            {
                                "ngram": "appraisals",
                                "importance": 238.06956521739133,
                                "contextualExtracts": [
                                    "https://www.xyz.com/shopping/antiques/appraisals",
                                    "https://www.xyz.com/home/g35180502/antique-appraisals",
                                ],
                            },
                        ],
                        "missingRowsPercent": 0.0,
                        "clusterName": "Cluster Y",
                    },
                ],
                "insightName": "importantNgrams",
            }
        ],
        "featureImpact": 0.8664601729230758,
    }


@pytest.fixture
def cluster_insights_geospatial_feature():
    return {
        "featureName": "zip_geometry (Centroid)",
        "featureType": "geospatialPoint",
        "insights": [
            {
                "perCluster": [
                    {
                        "representativeLocations": [
                            [-111.72777006911353, 40.28725705997828],
                            [-111.91177400221748, 40.33845396699792],
                            [-111.72777006911353, 40.28725705997828],
                            [-111.87330541678561, 40.41086871841134],
                            [-112.72171260615748, 40.626530363956824],
                            [-111.87330541678561, 40.41086871841134],
                            [-112.09854710008646, 40.5136818509972],
                            [-112.0797176051824, 41.081377393546205],
                            [-110.66026168011577, 40.355383869180145],
                            [-111.94606815201666, 40.70158256062799],
                            [-109.82278750113667, 40.94374160661019],
                            [-112.27336219040004, 40.55927459844233],
                            [-111.20110666634037, 40.36182430547487],
                            [-112.09854710008646, 40.5136818509972],
                            [-112.03762911624119, 40.60281875013827],
                            [-111.69697398575583, 40.22723683713423],
                            [-111.20110666634037, 40.36182430547487],
                            [-111.74310649332172, 40.557782939042404],
                            [-111.94444475677972, 40.495412641264764],
                            [-111.99656081537427, 40.32513383453981],
                            [-111.99656081537427, 40.32513383453981],
                            [-111.89075250205879, 40.61517738278862],
                            [-111.08251353081714, 40.77870569492425],
                            [-111.86741687854163, 40.500246056223816],
                            [-113.23307053933294, 37.09795393068157],
                            [-111.8424660195071, 40.795194319307456],
                            [-111.88444263752635, 40.65804122513974],
                            [-111.94444475677972, 40.495412641264764],
                            [-112.0797176051824, 41.081377393546205],
                            [-111.20110666634037, 40.36182430547487],
                            [-111.14475674299982, 40.641341483139556],
                            [-111.66648542881696, 41.6101251629629],
                            [-111.56511245718264, 40.115092182496454],
                            [-111.88506163621557, 40.93213120114122],
                            [-113.60823742626339, 37.175649462041804],
                            [-112.09854710008646, 40.5136818509972],
                            [-111.56861449793394, 40.06443884250683],
                            [-111.56511245718264, 40.115092182496454],
                            [-111.56861449793394, 40.06443884250683],
                            [-111.8132914517022, 40.677217699494726],
                            [-111.72777006911353, 40.28725705997828],
                            [-111.56861449793394, 40.06443884250683],
                            [-111.99656081537427, 40.32513383453981],
                            [-112.09854710008646, 40.5136818509972],
                            [-111.90360674214179, 40.98031543810573],
                            [-111.86741687854163, 40.500246056223816],
                            [-111.97890089199424, 40.55724377291889],
                            [-111.99656081537427, 40.32513383453981],
                            [-111.72449927945226, 40.34078298547955],
                            [-111.86741687854163, 40.500246056223816],
                            [-112.09854710008646, 40.5136818509972],
                            [-112.03762911624119, 40.60281875013827],
                            [-111.95053683033889, 41.0250502696615],
                            [-111.90252477230854, 41.194460915192515],
                            [-111.86725647578871, 40.86773606702239],
                            [-110.02868116238271, 40.329260196423874],
                            [-111.97890089199424, 40.55724377291889],
                            [-112.03762911624119, 40.60281875013827],
                            [-111.84948377782993, 41.335379694733035],
                            [-111.90252477230854, 41.194460915192515],
                            [-112.04637119080341, 41.37974345142534],
                            [-112.01342321770194, 40.65350463652058],
                            [-111.6981960823168, 40.62561339910202],
                            [-111.8173228297695, 39.295199653589385],
                            [-111.88444263752635, 40.65804122513974],
                            [-111.80693180163175, 41.775827696236696],
                            [-111.86741687854163, 40.500246056223816],
                            [-111.8132914517022, 40.677217699494726],
                            [-111.99278699761865, 41.72579315327621],
                            [-112.09854710008646, 40.5136818509972],
                            [-112.09854710008646, 40.5136818509972],
                            [-111.87330541678561, 40.41086871841134],
                            [-112.00120530319808, 40.69746934850137],
                            [-111.71039713962674, 40.31424607525435],
                            [-111.91177400221748, 40.33845396699792],
                            [-111.74310649332172, 40.557782939042404],
                            [-111.88444263752635, 40.65804122513974],
                            [-111.08251353081714, 40.77870569492425],
                            [-111.94444475677972, 40.495412641264764],
                            [-112.31806706636485, 41.76587827218204],
                            [-112.11645712394305, 41.270656133326504],
                            [-112.09854710008646, 40.5136818509972],
                            [-111.99656081537427, 40.32513383453981],
                            [-111.87330541678561, 40.41086871841134],
                            [-112.03814427877268, 41.218658170631144],
                            [-111.95053683033889, 41.0250502696615],
                            [-111.72777006911353, 40.28725705997828],
                            [-112.00120530319808, 40.69746934850137],
                            [-112.27336219040004, 40.55927459844233],
                            [-112.09854710008646, 40.5136818509972],
                            [-111.20110666634037, 40.36182430547487],
                            [-111.91696081859081, 40.8411449042637],
                            [-112.72171260615748, 40.626530363956824],
                            [-112.03814427877268, 41.218658170631144],
                            [-112.09854710008646, 40.5136818509972],
                            [-111.87330541678561, 40.41086871841134],
                            [-112.15590494017277, 40.71968494719153],
                            [-111.86213614439602, 40.57182358100957],
                            [-111.72777006911353, 40.28725705997828],
                            [-111.56861449793394, 40.06443884250683],
                            [-111.87330541678561, 40.41086871841134],
                            [-111.99656081537427, 40.32513383453981],
                            [-111.56511245718264, 40.115092182496454],
                            [-112.27336219040004, 40.55927459844233],
                            [-113.60823742626339, 37.175649462041804],
                            [-112.72171260615748, 40.626530363956824],
                            [-111.97890089199424, 40.55724377291889],
                            [-111.86821556425512, 39.01694151244415],
                            [-111.56861449793394, 40.06443884250683],
                            [-112.09854710008646, 40.5136818509972],
                            [-112.09854710008646, 40.5136818509972],
                            [-112.09854710008646, 40.5136818509972],
                            [-111.84948377782993, 41.335379694733035],
                            [-111.20110666634037, 40.36182430547487],
                            [-111.87330541678561, 40.41086871841134],
                            [-112.09854710008646, 40.5136818509972],
                            [-113.5581267117014, 37.046359693214626],
                            [-111.89269850711169, 40.714512977043576],
                            [-113.5581267117014, 37.046359693214626],
                            [-111.20110666634037, 40.36182430547487],
                            [-111.99656081537427, 40.32513383453981],
                            [-111.6981960823168, 40.62561339910202],
                            [-112.06122750508372, 41.12089120087726],
                            [-111.9761937794022, 41.32191963180718],
                            [-111.71915436449221, 40.4601732243208],
                        ],
                        "clusterName": "Cluster 1",
                    },
                    {
                        "representativeLocations": [
                            [-111.82855133506594, 40.59474159194577],
                            [-111.82855133506594, 40.59474159194577],
                        ],
                        "clusterName": "Cluster 2",
                    },
                    {
                        "representativeLocations": [
                            [-111.50183284923722, 40.6523637428088],
                            [-111.50183284923722, 40.6523637428088],
                            [-111.53431097580847, 40.73472565976418],
                            [-111.53431097580847, 40.73472565976418],
                            [-111.53431097580847, 40.73472565976418],
                            [-111.50183284923722, 40.6523637428088],
                            [-111.50183284923722, 40.6523637428088],
                            [-111.50183284923722, 40.6523637428088],
                            [-111.50183284923722, 40.6523637428088],
                            [-111.50183284923722, 40.6523637428088],
                            [-111.50183284923722, 40.6523637428088],
                            [-111.50183284923722, 40.6523637428088],
                            [-111.53431097580847, 40.73472565976418],
                            [-111.53431097580847, 40.73472565976418],
                            [-111.53431097580847, 40.73472565976418],
                            [-111.53431097580847, 40.73472565976418],
                            [-111.53431097580847, 40.73472565976418],
                            [-111.20110666634037, 40.36182430547487],
                            [-111.50984867449368, 40.52480835267078],
                            [-111.50183284923722, 40.6523637428088],
                        ],
                        "clusterName": "Cluster 3",
                    },
                    {
                        "representativeLocations": [
                            [-110.76030971731682, 39.54699891040753],
                            [-110.76030971731682, 39.54699891040753],
                            [-109.48291126636641, 40.62968575997615],
                            [-110.02868116238271, 40.329260196423874],
                            [-111.52781543934006, 42.76927083437281],
                            [-110.52755366280019, 40.13018282419259],
                            [-109.48291126636641, 40.62968575997615],
                            [-111.26807417396786, 42.32832684181201],
                            [-111.85954141551625, 40.738261272972196],
                            [-111.42070904612427, 42.216121714739124],
                            [-111.8424660195071, 40.795194319307456],
                            [-111.89269850711169, 40.714512977043576],
                            [-110.76030971731682, 39.54699891040753],
                            [-109.48291126636641, 40.62968575997615],
                            [-110.2754385331189, 40.35139578576289],
                            [-109.48291126636641, 40.62968575997615],
                            [-109.48291126636641, 40.62968575997615],
                            [-111.19802097976776, 39.329715712293606],
                            [-111.26807417396786, 42.32832684181201],
                            [-112.45834892391534, 42.1902572387958],
                            [-109.48291126636641, 40.62968575997615],
                            [-110.02868116238271, 40.329260196423874],
                            [-111.8839687847801, 40.75591126789004],
                            [-110.94508654245486, 42.1762672139657],
                            [-111.90002486631441, 40.7563908515508],
                        ],
                        "clusterName": "Cluster 4",
                    },
                ],
                "insightName": "representativeLocations",
            },
        ],
        "featureImpact": 13.7,
    }


@pytest.fixture
def cluster_insights_data(
    cluster_insights_numeric_feature,
    cluster_insights_categorical_feature,
    cluster_insights_image_feature,
    cluster_insights_text_feature,
    cluster_insights_geospatial_feature,
):
    return {
        "count": 5,
        "next": None,
        "previous": None,
        "data": [
            cluster_insights_numeric_feature,
            cluster_insights_categorical_feature,
            cluster_insights_image_feature,
            cluster_insights_text_feature,
            cluster_insights_geospatial_feature,
        ],
        "totalCount": 5,
        "version": 6,
    }


@pytest.fixture
def clustering_model_data(project_id, model_id):
    return {
        "blueprintId": "191cfe6abcba12895d0215b975fbd79d",
        "featurelistId": "617ac982c4884a7aaac49903",
        "featurelistName": "Informative Features",
        "id": model_id,
        "isFrozen": False,
        "isNClustersDynamicallyDetermined": False,
        "isStarred": False,
        "linkFunction": None,
        "metrics": {
            "Silhouette Score": {
                "validation": 0.30880001187324524,
                "crossValidation": None,
                "holdout": None,
                "training": 0.2850300073623657,
                "backtestingScores": None,
                "backtesting": None,
            }
        },
        "modelCategory": "model",
        "modelFamily": "CLUSTER",
        "modelNumber": 7,
        "modelType": "K-Means Clustering",
        "monotonicDecreasingFeaturelistId": None,
        "monotonicIncreasingFeaturelistId": None,
        "nClusters": 7,
        "parentModelId": None,
        "predictionThreshold": 0.5,
        "predictionThresholdReadOnly": False,
        "processes": [
            "One-Hot Encoding",
            "Truncated Singular Value Decomposition",
            "Missing Values Imputed",
            "No Image Augmentation",
            "Pretrained SqueezeNet Low-Level Generalized Mean Pooling Image Featurizer",
            "Matrix of word-grams occurrences",
            "Standardize",
            "K-Means Clustering",
        ],
        "projectId": project_id,
        "samplePct": 89.9885,
        "supportsComposableMl": False,
        "supportsMonotonicConstraints": False,
        "trainingDuration": None,
        "trainingEndDate": None,
        "trainingRowCount": 3110,
        "trainingStartDate": None,
    }
