import { fetcher } from "@/api/fetcher";
import { IPatentInfoModel } from "@/types/search"

export async function getPatentInfo(patentId: number): Promise<IPatentInfoModel> {
    const data = await fetcher("/report/info/?patent_id=" + patentId, { method: "GET" })
    console.log(data)
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