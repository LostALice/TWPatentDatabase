
import { Image } from "@heroui/react"
import {
  Table,
  TableHeader,
  TableBody,
  TableColumn,
  TableRow,
  TableCell,
  Link,
  Spinner
} from "@heroui/react";
import { userHistory } from "@/api/history"
import { getPatentInfo } from "@/api/patentId"
import { ISearchHistoryRecord, IUserHistoryRecord } from "@/types/history"
import DefaultLayout from "@/layouts/default";
import { useEffect, useState } from "react";

export default function SearchResultPage() {
  const [history, setHistory] = useState<ISearchHistoryRecord[]>([])
  const [patentInfoList, setPatentInfoList] = useState<IUserHistoryRecord[]>([])
  const [isDataLoading, setIsDataLoading] = useState(true);

  const columns = [
    { key: "Id", label: "ID" },
    { key: "Title", label: "標題" },
    { key: "PublicationNumber", label: "公開號" },
    { key: "ApplicationNumber", label: "申請號" },
    { key: "ApplicationDate", label: "申請日" },
    { key: "Applicant", label: "申請人" },
    { key: "SearchTime", label: "搜尋時間" },
  ];

  useEffect(() => {
    const getUserHistory = async () => {
      const userSearchHistory = await userHistory()

      const historyLog: IUserHistoryRecord[] = []
      for (const patent of userSearchHistory) {
        const patentData = await getPatentInfo(patent.patent_id)
        historyLog.push({
          patent_id: patent.patent_id,
          search_time: patent.search_time,
          Title: patentData.Title,
          ApplicationDate: patentData.ApplicationDate,
          PublicationDate: patentData.PublicationDate,
          ApplicationNumber: patentData.ApplicationNumber,
          PublicationNumber: patentData.PublicationNumber,
          Applicant: patentData.Applicant,
          Inventor: patentData.Inventor,
          Attorney: patentData.Attorney,
          Priority: patentData.Priority,
          GazetteIPC: patentData.GazetteIPC,
          IPC: patentData.IPC,
          GazetteVolume: patentData.GazetteVolume,
          KindCodes: patentData.KindCodes,
          PatentURL: patentData.PatentURL,
          PatentFilePath: patentData.PatentFilePath,
        })
      }
      
      setPatentInfoList(historyLog)
      setHistory(userSearchHistory)
    }
    
    getUserHistory()
    setIsDataLoading(false)
  }, [])
  return (
    <DefaultLayout>
      <div className="p-8">
        <div className="flex justify-between items-center mb-6">
          <Image
            alt="Pou Chen Group"
            src="https://www.pouchen.com/images/logo.png"
          />
          歷史紀錄
        </div>

        <Table aria-label="Table of searching history">
          <TableHeader columns={columns}>
            {(column) => (
              <TableColumn key={column.key} allowsSorting>
                {column.label}
              </TableColumn>
            )}
          </TableHeader>
          <TableBody
            items={patentInfoList}
            isLoading={isDataLoading}
            loadingContent={<Spinner label="Loading..." />}
          >
            {(item) => (
              <TableRow key={item.search_time} className="">
                <TableCell className="px-6 py-4 whitespace-normal text-sm">
                  {item.patent_id}
                </TableCell>
                <TableCell className="px-6 py-4 whitespace-normal text-sm truncate ">
                  <Link
                    anchorIcon={true}
                    href={"result/" + item.patent_id}
                  >
                    {item.Title}
                  </Link>
                </TableCell>
                <TableCell className="px-6 py-4 whitespace-normal text-sm">
                  {item.PublicationNumber}
                </TableCell>
                <TableCell className="px-6 py-4 whitespace-normal text-sm">
                  {item.ApplicationNumber}
                </TableCell>
                <TableCell className="px-6 py-4 whitespace-normal text-sm">
                  {item.ApplicationDate}
                </TableCell>
                <TableCell className="px-6 py-4 whitespace-normal text-sm truncate ">
                  {item.Applicant}
                </TableCell>
                <TableCell className="px-6 py-4 whitespace-normal text-sm truncate ">
                  {item.search_time.split(".")[0]}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </DefaultLayout>
  );
}
