from enum import Enum


class ModelColor(Enum):
    """Model colors."""

    BLUE = "blue"
    ARCTIC_BLUE = "arctic_blue"
    GREEN = "green"
    TURQUOISE = "turquoise"
    PINK = "pink"
    PURPLE = "purple"
    YELLOW = "yellow"
    RED = "red"


class ModelIcon(Enum):
    """Model Icons."""

    GENERAL = "general"
    CHURN_AND_RETENTION = "churn-and-retention"
    CONVERSION_PREDICT = "conversion-predict"
    ANOMALY = "anomaly"
    DYNAMIC_PRICING = "dynamic-pricing"
    EMAIL_FILTERING = "email-filtering"
    DEMAND_FORECASTING = "demand-forecasting"
    LTV = "ltv"
    PERSONALIZATION = "personalization"
    FRAUD_DETECTION = "fraud-detection"
    CREDIT_RISK = "credit-risk"
    RECOMMENDATIONS = "recommendations"
