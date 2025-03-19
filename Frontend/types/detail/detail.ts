export interface IPatentInformation {
  id: string;
  name: string;
  applicant: string;
  risk: string;
  keyword: string;
  description: string;
  location: string;
  keywords?: string[] | string;
}
