import PolicyEngineFooter from "../src/components/PolicyEngineFooter";
import PolicyEngineHeader from "../src/components/PolicyEngineHeader";

import "./globals.css";
import Script from "next/script";

export const metadata = {
  title: "Energy, fuel and food price rises and UK households, 2027-28 | PolicyEngine",
  description:
    "Interactive dashboard modelling the impact of energy price shocks from Middle East supply disruption on UK household living standards using PolicyEngine microsimulation.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <PolicyEngineHeader />
        {children}
        <PolicyEngineFooter />
        {/* Google Analytics: policyengine.org's GA4 property; this app is served at
            policyengine.org/uk/middle-east-war-living-standards through a rewrite, where the main site's GA
            does not reach. Page views only. */}
        {process.env.NODE_ENV === "production" && (
          <>
            <Script
              src="https://www.googletagmanager.com/gtag/js?id=G-2YHG89FY0N"
              strategy="afterInteractive"
            />
            <Script id="google-analytics" strategy="afterInteractive">
              {`window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-2YHG89FY0N');`}
            </Script>
          </>
        )}
      </body>
    </html>
  );
}
