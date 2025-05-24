// Code by AkinoAlice@TyrantRey

import { fetcher } from "./fetcher";
import { LoginCertificate } from "@/types/login"

export const userLogin = async (username: string, password: string): Promise<LoginCertificate | null> => {
    const resp = await fetcher("/authorization/login/", {
        method: "POST",
        body: JSON.stringify({
            username: username,
            password: password,
        })
    });
    const data = await resp;

    if (data != false) {
        return {
            access_token: data.access_token,
            refresh_token: data.refresh_token,
        };
    } else {
        return null;
    }
}