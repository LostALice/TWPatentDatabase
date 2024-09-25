# Code by AkinoAlice@TyrantRey

from datetime import datetime
import types


class PatentInfo(object):
    ApplicationDate: int
    PublicationDate: int
    ApplicationNumber: str
    PublicationNumber: str
    Applicant: str
    Inventor: str
    Attorney: str
    Priority: str
    GazetteIPC: str
    IPC: str
    GazetteVolume: str
    KindCodes: str
