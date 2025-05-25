// Code by AkinoAlice@TyrantRey
import { fetcher } from "./fetcher";
import { IPatentInfoModel } from "@/types/search"

export async function fullTextSearch(searchParse: string): Promise<IPatentInfoModel[]> {
    const data = await fetcher("/search/full-text/?search_keywords=" + encodeURIComponent(searchParse), {
        method: "GET"
    })

    const patents: IPatentInfoModel[] = []
    for (const patent of data.patents) {
        patents.push(
            {
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
                Patent_id: patent.Patent_id,
            }
        )
    }

    console.log(patents)
    return patents
}

export async function similaritySearch(searchParse: string): Promise<string> {
    const data = await fetcher("/response/search/?query=" + encodeURIComponent(searchParse), {
        method: "GET"
    })

    return data
}

export async function startScraper(searchParse: string) {
    console.log(searchParse)
    const data = await fetcher("/search/scraper/?" + new URLSearchParams({ patent_keyword: searchParse }), {
        method: "POST",
    })

    return data
}