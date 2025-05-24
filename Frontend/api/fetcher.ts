// Code by AkinoAlice@TyrantRey
// fetch wrapper

import { deleteCookie } from "cookies-next";
import { addToast } from "@heroui/react";
import Router from "next/router";
import { siteConfig } from "@/config/site";

export interface FetchOptions extends RequestInit {
  headers?: HeadersInit;
}

export async function fetcher(
  url: string,
  options: FetchOptions = {},
): Promise<any> {
  const defaultOptions: FetchOptions = {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  };
  const response = await fetch(siteConfig.baseURL + url, { ...defaultOptions, ...options });
  const data = response.json();

  if (response.status >= 400) {
    deleteCookie("refresh_token");
    deleteCookie("access_token");

    Router.replace("/login");
    return false;
  }

  return data;
}
