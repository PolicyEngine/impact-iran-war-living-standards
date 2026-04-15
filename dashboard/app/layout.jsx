import "./globals.css";

export const metadata = {
  title: "Energy Price Shock: Impact on UK Living Standards | PolicyEngine",
  description:
    "Interactive dashboard modelling the impact of energy price shocks from Middle East supply disruption on UK household living standards using PolicyEngine microsimulation.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
