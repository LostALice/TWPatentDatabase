type TRisk = "低" | "中" | "高";

export interface ISearchResults {
  id: string;
  name: string;
  applicant: string;
  risk: TRisk;
  keyword?: string[];
  report?: string;
}
