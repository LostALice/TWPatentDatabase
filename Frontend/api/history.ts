// Code by AkinoAlice@TyrantRey

import { fetcher } from "./fetcher";
import { ISearchHistoryRecord } from "@/types/history"

export async function userHistory(): Promise<ISearchHistoryRecord[]> {
    const data = await fetcher("/history/search/")
    console.log(data)

    return data.map((history: ISearchHistoryRecord) => ({
        patent_id: history.patent_id,
        search_time: history.search_time,
    }));
}

export async function searchPatents(patentIds: number[]) {
    const data = await fetcher("/history/search/")
}
