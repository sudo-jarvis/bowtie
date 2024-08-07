import { useMemo } from "react";

import CasesSection from "./components/Cases/CasesSection";
import RunInfoSection from "./components/RunInfo/RunInfoSection";
import SummarySection from "./components/Summary/SummarySection";
import Implementation from "./data/Implementation.ts";
import { FilterSection } from "./components/FilterSection.tsx";
import { useSearchParams } from "./hooks/useSearchParams.ts";
import { BenchmarkReportData } from "./data/parseBenchmarkData.ts";
import BenchmarkRunInfoSection from "./components/RunInfo/BenchmarkRunInfoSection.tsx";

export const BenchmarkReportView = ({
  benchmarkReportData,
  topPageInfoSection,
  allImplementationsData,
}: {
  benchmarkReportData: BenchmarkReportData;
  topPageInfoSection?: React.ReactElement;
  allImplementationsData: Map<string, Implementation>;
}) => {
  const params = useSearchParams();
//   const languages = useMemo(() => {
//     const langs = new Set<string>();
//     for (const each of benchmarkReportData.metadata.implementations.values()) {
//       langs.add(each.language);
//     }
//     return Array.from(langs);
//   }, [benchmarkReportData]);

//   const filteredReportData = useMemo(() => {
//     const filteredData = { ...benchmarkReportData };
//     const selectedLanguages = params.getAll("language");

//     // if (selectedLanguages.length > 0) {
//     //   const filteredReportArray = Array.from(
//     //     reportData.implementationsResults.entries(),
//     //   ).filter(([id]) =>
//     //     selectedLanguages.includes(
//     //       reportData.runMetadata.implementations.get(id)!.language,
//     //     ),
//     //   );
//     //   filteredData.implementationsResults = new Map(filteredReportArray);
//     // }

//     return filteredData;
//   }, [benchmarkReportData, params]);

//   const filteredOtherImplementationsData = useMemo(() => {
//     const selectedLanguages = params.getAll("language");
//     const availableLanguages =
//       selectedLanguages.length > 0 ? selectedLanguages : languages;

//     return new Map(
//       Array.from(allImplementationsData)
//         .filter(([, impl]) => availableLanguages.includes(impl.language))
//         .filter(([key]) => !filteredReportData.implementationsResults.has(key)),
//     );
//   }, [params, allImplementationsData, languages, filteredReportData]);

  return (
    <main className="container-lg">
      <div className="col col-lg-8 mx-auto">
        {topPageInfoSection}
        <BenchmarkRunInfoSection benchmarkRunMetadata={benchmarkReportData.metadata} />
        {/* <FilterSection languages={languages} />
        <SummarySection
          reportData={filteredReportData}
          otherImplementationsData={filteredOtherImplementationsData}
        />
        <CasesSection reportData={filteredReportData} /> */}
      </div>
    </main>
  );
};
