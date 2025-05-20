# Code by AkinoAlice@TyrantRey

from pydantic import BaseModel


class PatentModel(BaseModel):
    Title: str = ""
    ApplicationDate: int = 0
    PublicationDate: int = 0
    ApplicationNumber: str = ""
    PublicationNumber: str = ""
    Applicant: str = ""
    Inventor: str = ""
    Attorney: str = ""
    Priority: str = ""
    GazetteIPC: str = ""
    IPC: str = ""
    GazetteVolume: str = ""
    KindCodes: str = ""
    PatentURL: str = ""
    PatentFilePath: str = ""


class PatentInfoModel(PatentModel):
    Patent_id: int


class PatentImageModel(BaseModel):
    image_path: str
    page: int


class PatentImageInfoModel(BaseModel):
    patent_serial: str
    image_list: list[PatentImageModel]
