
import { Image, Button, Link } from "@heroui/react"
import {
  Table,
  TableHeader,
  TableBody,
  TableColumn,
  TableRow,
  TableCell
} from "@heroui/table";

import DefaultLayout from "@/layouts/default";
import { ISearchResults } from "@/types/results"

const searchResults_: ISearchResults[] = [
  {
    id: "TW202506022A",
    name: "電容式足部感應",
    applicant: "NIKE INNOVATE C.V.",
    risk: "高",
    keyword: ["電容"],
  },
  {
    id: "TW202506022B",
    name: "針織鞋面技術",
    applicant: "NIKE INNOVATE C.V.",
    risk: "中",
    keyword: ["針織"],
  },
  {
    id: "TW202505914B",
    name: "鞋履便捷穿脫設計",
    applicant: "SKECHERS U.S.A.",
    risk: "低",
    keyword: ["便捷"],
  },
];

export default function SearchResultPage() {
  return (
    <DefaultLayout>
      <div className="p-8">
        <div className="flex justify-between items-center mb-6">
          <Image
            alt="Pou Chen Group"
            src="https://www.pouchen.com/images/logo.png"
          />
          <Button 
          as={Link}
          className="px-4 py-2"
          href="/history"
          >
            搜尋歷史
          </Button>
        </div>

        <Table aria-label="Table of searching history">
          <TableHeader>
            <TableColumn>公開公告號</TableColumn>
            <TableColumn>專利名稱</TableColumn>
            <TableColumn>申請人</TableColumn>
            <TableColumn>侵權程度</TableColumn>
            <TableColumn>相關專利名稱</TableColumn>
            <TableColumn>侵權風險報告</TableColumn>
          </TableHeader>
          <TableBody>
            {searchResults_.map((result, index) => (
              <TableRow key={index}>
                <TableCell>{result.id}</TableCell>
                <TableCell>{result.name}</TableCell>
                <TableCell>{result.applicant}</TableCell>
                <TableCell>{result.risk}</TableCell>
                <TableCell>{result.keyword}</TableCell>
                <TableCell>
                  <Link
                    href={"/detail/" + (index + 1)}
                  >
                    {result.id}
                  </Link>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </DefaultLayout>
  );
}
