

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
import { IPatentInfoModel } from "@/types/search"

export const PatentTable = ({ patents }: { patents: IPatentInfoModel[] }) => {
    const columns = [
        { key: "Id", label: "ID" },
        { key: "Title", label: "標題" },
        { key: "PublicationNumber", label: "公開號" },
        { key: "ApplicationNumber", label: "申請號" },
        { key: "ApplicationDate", label: "申請日" },
        { key: "Applicant", label: "申請人" },
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
                    <TableRow key={item.Patent_id}>
                        <TableCell className="px-6 py-4 whitespace-normal text-sm">
                            {item.Patent_id}
                        </TableCell>
                        <TableCell className="px-6 py-4 whitespace-normal text-sm">
                            <Link
                                href={"result/" + item.Patent_id}
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
                        <TableCell className="px-6 py-4 whitespace-normal text-sm">
                            {item.Applicant}
                        </TableCell>
                    </TableRow>
                )}
            </TableBody>
        </Table>
    )
}