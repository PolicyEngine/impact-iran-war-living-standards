import "./globals.css";

export const metadata = {
  title: "Impact of the Middle East War on UK Living Standards | PolicyEngine",
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
