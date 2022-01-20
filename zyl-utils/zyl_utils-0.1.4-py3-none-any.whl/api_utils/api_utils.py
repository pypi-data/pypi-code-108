# encoding: utf-8
'''
@author: zyl
@file: api_utils.py
@time: 2021/11/8 17:48
@desc:
'''
from enum import Enum
from typing import List, Set, Optional, Dict, Union

from fastapi import Body, FastAPI, Query
from fastapi import Depends  # depends依赖项
from fastapi import File, UploadFile
from fastapi import Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, EmailStr

# use html #############################################
# app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")
# templates = Jinja2Templates(directory="templates")
# @app.get("/items/{id}", response_class=HTMLResponse)
# async def read_item(request: Request, id: str):
#     return templates.TemplateResponse("demo.html", {"request": request, "id": id})
# #####################################

# 1. 实例化接口#################################
app = FastAPI(title="Fastapi",
              version="0.0.1",
              contact={
                  "name": "张玉良",
                  "url": "https://github.com/ZYuliang/",
                  "email": "1137379695@qq.com",
              },

              license_info={
                  "name": "Apache 2.0",
                  "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
              },
              description="项目描述，接口说明，日志更新记录",
              openapi_tags=[
                  {
                      "name": "interface1",
                      "description": "接口1说明",
                  },
                  {
                      "name": "interface2",
                      "description": "接口2说明",
                      "externalDocs": {
                          "description": "添加外部文档说明",
                          "url": "https://fastapi.tiangolo.com/",
                      },
                  },
              ],
              )


# 2.定义输入输出##############################
class RequestItem(str, Enum):
    name: str = Field(..., example="Foo", title="The description of the item", max_length=300, alias="other_name",
                      description="Query string  for the items to search in the database that have a good match",
                      regex=None)

    num: Optional[float] = Query(..., min_length=3)

    # image: Optional[List[Image]] = None
    tags: Set[str] = set()


class ResponseItem(BaseModel):
    url: str
    name: str


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class Image(BaseModel):
    url: str
    name: str


# 请求体---参数类型，默认值，限制，描述
class Item(BaseModel):
    # 当一个属性具有默认值时，它不是必需的。否则它是一个必需属性。item.dict()
    name: str = Field(..., example="Foo")
    description: Optional[str] = None  # 可选参数，默认值为None
    price: float
    tax: Optional[float] = None
    q: str = Query(..., min_length=3)  # ... 表示必须参数
    q2: List[str] = Query(["foo", "bar"])  # Query检验
    q3: list = Query([])
    q4: Optional[str] = Query(
        None,
        alias="item-query",  # 别名
        title="Query string",  # 标题
        description="Query string  for the items to search in the database that have a good match",  # 描述
        min_length=3,
        deprecated=True,  # 表明该参数已经弃用
        regex="^fixedquery$"  # 字符串正则表达式
    )
    size: float = Query(..., gt=0, lt=10.5)  # int，float。大于小于设置

    description2: Optional[str] = Field(
        None, title="The description of the item", max_length=300
    )
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    tags: Set[str] = set()

    image: Optional[List[Image]] = None  # 子请求体

    # 例子
    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            }
        }


class User(BaseModel):
    username: str
    full_name: Optional[str] = None


class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: Optional[str] = None


class BaseItem(BaseModel):
    description: str
    type: str


class CarItem(BaseItem):
    type = "car"


class PlaneItem(BaseItem):
    type = "plane"
    size: int


# 3.接口函数 #####################################

# response_model_exclude_unset=True响应中将不会包含那些默认值，而是仅有实际设置的值 或者response_model_include={"name", "description"}
@app.post("/items/", response_model=UserIn, response_model_exclude_unset=True)
async def create_item(item: Item, img: List[Image], weights: Dict[int, float], importance: int = Body(...),
                      response_model=Union[PlaneItem, CarItem], status_code=201):
    print(item.dict())
    return item


@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    # 通过表单字段发送 username 和 password
    return {"username": username}


@app.post("/files/")
async def create_file(file: bytes = File(...)):  # 以 bytes 形式读取和接收文件内容
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):  # 更适于处理图像、视频、二进制文件等大型文件，好处是不会占用所有内存
    # filename：上传文件名字符串（str），例如， myimage.jpg；
    # content_type：内容类型（MIME类型 / 媒体类型）字符串（str），例如，image / jpeg；
    # file： SpooledTemporaryFile（ file - like对象）。其实就是Python文件，可直接传递给其他预期file - like对象的函数或支持库。
    # UploadFile支持以下 async 方法，（使用内部SpooledTemporaryFile）可调用相应的文件方法。
    # write(data)：把data （str或bytes）写入文件；
    # read(size)：按指定数量的字节或字符（size(int)）读取文件内容；
    # seek(offset)：移动至文件offset （int）字节处的位置；例如，await myfile.seek(0)移动到文件开头；执行
    # await myfile.read()后，需再次读取已读取内容时，这种方法特别好用；
    # close()：关闭文件。

    contents = await file.read()  # 或contents = myfile.file.read()
    return {"filename": file.filename}


@app.post("/files/", tags=["items"], summary="Create an item",
          description="Create an item with all the information, name, description, price, tax and a set of unique tags",
          response_description="The created item", deprecated=True)
# tags 相当于改url所属的区域或者说是类型，不同url块
# summary对url的总结
# description对url的描述):
# response_description返回描述
# , deprecated=True弃用的接口
async def create_files(files: List[bytes] = File(...)):
    """
        直接写在这里面的是接口的描述，用markdown
       Create an item with all the information:

       - **name**: each item must have a name
       - **description**: a long description
       - **price**: required
       - **tax**: if the item doesn't have tax, you can omit this
       - **tags**: a set of unique tag strings for this item
       """
    return {"file_sizes": [len(file) for file in files]}


@app.get("/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


async def common_parameters(q: Optional[str] = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons


# 4.测试###############################
# from fastapi.testclient import TestClient
#
# from .main import app
#
# client = TestClient(app)
#
# def test_read_main():
#     response = client.get("/")
#     assert response.status_code == 200
#     assert response.json() == {"msg": "Hello World"}

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3243)
