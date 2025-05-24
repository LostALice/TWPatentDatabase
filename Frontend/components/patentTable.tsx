

import {
    Table,
    TableHeader,
    TableColumn,
    TableBody,
    TableRow,
    TableCell,
    Button,
    Link
} from "@heroui/react";
import { PatentInfoModel } from "@/types/search"

const test = {
    "Title": "發泡體FOAM",
    "ApplicationDate": 20240822,
    "PublicationDate": 20250301,
    "ApplicationNumber": "TW113131578",
    "PublicationNumber": "TW202509128A",
    "Applicant": "財團法人工業技術研究院 新竹縣竹東鎮中興路4段195號 (中華民國);\nINDUSTRIAL TECHNOLOGY RESEARCH INSTITUTE 195, SEC. 4, CHUNG HSING RD., CHUTUNG, HSINCHU, 310401, TAIWAN, R.O.C. (TW)",
    "Inventor": "吳晉安 (中華民國); WU, JIN-AN (TW);\n吳志郎 (中華民國); WU, CHIN-LANG (TW);\n張勝隆 (中華民國); CHANG, SHENG-LUNG (TW);\n陳建明 (中華民國); CHEN, CHIEN-MING (TW)",
    "Attorney": "洪澄文; 洪茂",
    "Priority": "美國 63/578,430 20230824",
    "GazetteIPC": "C08J 9/12(2006.01); B29D 35/00(2010.01); C08G 81/00(2006.01); C08K 5/098(2006.01); C08L 67/02(2006.01); C08L 71/00(2006.01)",
    "IPC": "C08J 9/12(2006.01); B29D 35/00(2010.01); C08G 81/00(2006.01); C08K 5/098(2006.01); C08L 67/02(2006.01); C08L 71/00(2006.01)",
    "GazetteVolume": "23-05",
    "KindCodes": "A",
    "PatentURL": "https://tiponet.tipo.gov.tw/gpss4/gpsskmc/gpssbkm?.86e60C5820010000000AD200000000^2100000001000000000000010203A04cdd",
    "PatentFilePath": "./patent/TWAN-202509128.pdf",
    "Patent_id": 10
}

export const PatentTable = ({ patents }: { patents: PatentInfoModel[] }) => {
    const columns = [
        { key: "Id", label: "ID" },
        { key: "Title", label: "標題" },
        // { key: "ApplicationDate", label: "申請日期" },
        // { key: "PublicationDate", label: "公開日期" },
        { key: "ApplicationNumber", label: "申請號" },
        { key: "PublicationNumber", label: "公開號" },
        // { key: "Applicant", label: "申請人" },
        // { key: "Inventor", label: "發明人" },
        // { key: "Attorney", label: "代理人" },
        // { key: "Priority", label: "優先權" },
        // { key: "GazetteIPC", label: "公報IPC" },
        // { key: "IPC", label: "IPC" },
        // { key: "GazetteVolume", label: "公報卷期" },
        // { key: "KindCodes", label: "種類碼" },
        // { key: "PatentURL", label: "專利網址" },
        // { key: "PatentFilePath", label: "專利文件路徑" },
        { key: "view", label: "查看專利" },
    ];

    return (
        <Table aria-label="專利資訊表格" className="min-w-full py-3">
            <TableHeader columns={columns}>
                {(column) => (
                    <TableColumn key={column.key} >
                        {column.label}
                    </TableColumn>
                )}
            </TableHeader>
            <TableBody items={patents}>
                {(item) => (
                    <TableRow key={item.Patent_id} className="">
                        <TableCell className="px-6 py-4 whitespace-normal text-sm">
                            {item.Patent_id}
                        </TableCell>
                        <TableCell className="px-6 py-4 whitespace-normal text-sm">
                            {item.Title}
                        </TableCell>
                        <TableCell className="px-6 py-4 whitespace-normal text-sm">
                            {item.ApplicationNumber}
                        </TableCell>
                        <TableCell className="px-6 py-4 whitespace-normal text-sm">
                            {item.PublicationNumber}
                        </TableCell>
                        <TableCell className="px-6 py-4 whitespace-normal text-sm">
                            <Button
                                as={Link}
                                href={"/result/" + item.Patent_id}
                            >
                                查看專利
                            </Button>
                        </TableCell>
                    </TableRow>
                )}
            </TableBody>
        </Table>
    )
}