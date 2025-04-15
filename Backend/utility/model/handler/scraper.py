# Code by AkinoAlice@TyrantRey

from pydantic import BaseModel


class PatentInfo(BaseModel):
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
