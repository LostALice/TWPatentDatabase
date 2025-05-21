// Code by AkinoAlice@TyrantRey
// fetch wrapper

export async function fetcher(url: string, prams: any) {
  const apiURL = "http://localhost:8000" + url;
  const resp = await fetch(apiURL, {});

  return resp.json();
}
