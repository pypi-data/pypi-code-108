from pymongo.collection import Collection

product_collection: Collection = None
coupon_collection: Collection = None
discount_collection: Collection = None
user_collection: Collection = None
user_profile_collection: Collection = None
private_profile_collection: Collection = None
cart_collection: Collection = None


def set_collections(
    product: Collection,
    coupon: Collection,
    discount: Collection,
    user: Collection,
    user_profile: Collection,
    private_profile: Collection,
    cart: Collection,
) -> None:
    global product_collection
    global coupon_collection
    global discount_collection
    global user_collection
    global user_profile_collection
    global private_profile_collection
    global cart_collection
    product_collection = product
    coupon_collection = coupon
    discount_collection = discount
    user_collection = user
    user_profile_collection = user_profile
    private_profile_collection = private_profile
    cart_collection = cart


def get_collection(name: str) -> Collection:
    if name == "product":
        return product_collection
    if name == "coupon":
        return coupon_collection
    if name == "discount":
        return discount_collection
    if name == "user":
        return user_collection
    if name == "cart":
        return cart_collection
    if name == "user_profile":
        return user_profile_collection
    if name == "private_profile":
        return private_profile_collection
