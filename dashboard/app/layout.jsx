import "./globals.css";

export const metadata = {
  title: "Iran Conflict: Impact on UK Living Standards | PolicyEngine",
  description:
    "Interactive dashboard modelling the impact of an Iran conflict on UK household living standards through energy, fuel, and food price shocks using PolicyEngine microsimulation.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
