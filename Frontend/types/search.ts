// Code by AkinoAlice@TyrantRey

export interface PatentModel {
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

export interface PatentInfoModel extends PatentModel {
    Patent_id: number
}

export interface PatentImageModel {
    image_path: string
    page: number
}


export interface PatentImageInfoModel {
    patent_serial: string
    image_list: [PatentImageModel]
}


export interface SearchResult {
    patents: PatentInfoModel
    search_time: string
}