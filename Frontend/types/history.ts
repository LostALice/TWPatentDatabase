// Code by AkinoAlice@TyrantRey

import { IPatentModel } from "@/types/search"

export interface ISearchHistoryRecord {
    patent_id: number;
    search_time: string
}

export interface IUserHistoryRecord extends ISearchHistoryRecord, IPatentModel {}