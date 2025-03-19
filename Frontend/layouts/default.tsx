import { Head } from "./head";

import { Navbar } from "@/components/navbar";
import Transition from "@/components/transition/transition";


export default function DefaultLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative flex flex-col h-screen">
      <Head />
      <Navbar />
      <main className="container mx-auto max-w-7xl px-6 flex-grow pt-16">
        <Transition>
          {children}
        </Transition>
      </main>
    </div>
  );
}
