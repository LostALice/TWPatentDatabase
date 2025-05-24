// Code by AkinoAlice@TyrantRey

import { fetcher } from "./fetcher";


export async function verifyLogin(): Promise<boolean> {

    const resp = await fetcher("/authorization/verify/")
    console.log(resp)

    return true;
}