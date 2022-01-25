from typing import List

from pydantic import BaseModel


hexstr = str


class Payload(BaseModel):
    type: int
    index: hexstr
    data: hexstr


class PayloadContent(BaseModel):
    index: str
    data: str


class SignedData(BaseModel):
    data: str
    signature: str


class MessageData(BaseModel):
    networkId: str
    parentMessageIds: List[hexstr]
    payload: Payload
    nonce: str


class MessageResp(BaseModel):
    data: MessageData


class CreateMessageData(BaseModel):
    messageId: hexstr


class CreateMessageResp(BaseModel):
    data: CreateMessageData


class SearchMessageData(BaseModel):
    index: hexstr
    maxResults: int
    count: int
    messageIds: List[hexstr]


class SearchMessageResp(BaseModel):
    data: SearchMessageData
