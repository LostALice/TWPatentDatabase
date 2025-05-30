import { fetcher } from "@/api/fetcher";
import { IPatentInfoModel } from "@/types/search"

export async function getPatentInfo(patentId: number): Promise<IPatentInfoModel> {
    const data = await fetcher("/report/info/?patent_id=" + patentId, { method: "GET" })
    return {
        Patent_id: data.Patent_id,
        Title: data.Title,
        ApplicationDate: data.ApplicationDate,
        PublicationDate: data.PublicationDate,
        ApplicationNumber: data.ApplicationNumber,
        PublicationNumber: data.PublicationNumber,
        Applicant: data.Applicant,
        Inventor: data.Inventor,
        Attorney: data.Attorney,
        Priority: data.Priority,
        GazetteIPC: data.GazetteIPC,
        IPC: data.IPC,
        GazetteVolume: data.GazetteVolume,
        KindCodes: data.KindCodes,
        PatentURL: data.PatentURL,
        PatentFilePath: data.PatentFilePath,
    }
}

export async function generateInfringementPatent(patentId: number): Promise<string> {
    return await fetcher("/response/summary/?patent_id=" + patentId, { method: "GET" })
}

export async function generatePatentGraph(patentId: number): Promise<IPatentInfoModel[]> {
    const data = await fetcher("/search/graph/?patent_id=" + patentId, { method: "GET" })

    return data.map((patent: IPatentInfoModel) => {
        return {
            Patent_id: patent.Patent_id,
            Title: patent.Title,
            ApplicationDate: patent.ApplicationDate,
            PublicationDate: patent.PublicationDate,
            ApplicationNumber: patent.ApplicationNumber,
            PublicationNumber: patent.PublicationNumber,
            Applicant: patent.Applicant,
            Inventor: patent.Inventor,
            Attorney: patent.Attorney,
            Priority: patent.Priority,
            GazetteIPC: patent.GazetteIPC,
            IPC: patent.IPC,
            GazetteVolume: patent.GazetteVolume,
            KindCodes: patent.KindCodes,
            PatentURL: patent.PatentURL,
            PatentFilePath: patent.PatentFilePath,
        }
    })
}