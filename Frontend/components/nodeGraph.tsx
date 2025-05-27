// Code by AkinoAlice@TyrantRey

import Graph from "react-vis-ts";
import { IPatentInfoModel } from "@/types/search";
import { useRouter } from "next/navigation";



export function PatentGraph({ patentData, centerPatentId }: { patentData: IPatentInfoModel[], centerPatentId: number }) {
    const router = useRouter()
    const node = patentData.map((patentData) => {
        return {
            id: patentData.Patent_id,
            label: patentData.Title,
            title: patentData.Title,
        }
    })
    const edge = patentData
        .filter(p => p.Patent_id !== centerPatentId)
        .map(p => ({
            from: centerPatentId,
            to: p.Patent_id,
            length: 250
        }))

    const graph = {
        nodes: node,
        edges: edge
    };

    return <Graph className="h-max" graph={graph}
        events={{
            selectEdge: (event: any) => {
                console.log(event)
                router.replace("/result/" + event.nodes[0])
            }
        }}
    />
}
