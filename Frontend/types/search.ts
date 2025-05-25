// Code by AkinoAlice@TyrantRey

export interface IPatentModel {
    Title: string
    ApplicationDate: number
    PublicationDate: number
    ApplicationNumber: string
    PublicationNumber: string
    Applicant: string
    Inventor: string
    Attorney: string
    Priority: string
    GazetteIPC: string
    IPC: string
    GazetteVolume: string
    KindCodes: string
    PatentURL: string
    PatentFilePath: string
}

export interface IPatentInfoModel extends IPatentModel {
    Patent_id: number
}

export interface IPatentImageModel {
    image_path: string
    page: number
}


export interface IPatentImageInfoModel {
    patent_serial: string
    image_list: [IPatentImageModel]
}


export interface ISearchResult {
    patents: IPatentInfoModel
    search_time: string
}