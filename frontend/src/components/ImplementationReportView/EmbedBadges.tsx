import React, { useState } from "react";
import { Accordion, Badge, Nav, Tab } from "react-bootstrap";
import { Implementation } from "../../data/parseReportData";
import CopyToClipboard from "../CopyToClipboard";
import Dialect from "../../data/Dialect";
import { reportUri } from "../../data/ReportHost";

const EmbedBadges: React.FC<{
  implementation: Implementation;
}> = ({ implementation }) => {
  const reportURIpath: string = reportUri.href();
  const results = Object.entries(implementation.results);
  const [activeTab, setActiveTab] = useState("URL");
  const [activeDialect, setActiveDialect] = useState(results[0][0]);

  const generateBadgeURI = (dialect: string): string => {
    return `https://img.shields.io/endpoint?url=${encodeURIComponent(
      `${reportURIpath}badges/${implementation.language}-${
        implementation.name
      }/compliance/${Dialect.forPath(dialect).path}.json`
    )}`;
  };

  const handleSelectDialect = (dialect: string): void => {
    setActiveDialect(dialect);
    setBadgeURI(generateBadgeURI(dialect));
  };

  const [badgeURI, setBadgeURI] = useState(generateBadgeURI(activeDialect));

  const handleSelect = (tabKey: string | null) => {
    if (tabKey) {
      setActiveTab(tabKey);
    }
  };

  return (
    <Accordion className="mx-auto mb-3 col-md-9">
      <Accordion.Item eventKey="0">
        <Accordion.Header>Embed Badge</Accordion.Header>
        <Accordion.Body>
          <div className="container d-flex justify-content-center flex-row flex-wrap">
            {results.map((result) => (
              <Badge
                pill
                bg={result[0] === activeDialect ? `filter-active` : `filter`}
                key={result[0]}
                className="mx-1 mb-2"
                onClick={() => handleSelectDialect(result[0])}
                role="button"
              >
                <div className="px-2">{result[0]}</div>
              </Badge>
            ))}
          </div>

          <div className="container d-flex justify-content-center align-items-center flex-column">
            <Tab.Container defaultActiveKey="URL">
              <Nav
                className="justify-content-center gap-2"
                variant="pills"
                activeKey={activeTab}
                onSelect={handleSelect}
              >
                <Nav.Item>
                  <Nav.Link eventKey="URL">URL</Nav.Link>
                </Nav.Item>
                <Nav.Item>
                  <Nav.Link eventKey="Markdown">Markdown</Nav.Link>
                </Nav.Item>
                <Nav.Item>
                  <Nav.Link eventKey="rSt">rSt</Nav.Link>
                </Nav.Item>
                <Nav.Item>
                  <Nav.Link eventKey="AsciiDoc">AsciiDoc</Nav.Link>
                </Nav.Item>
                <Nav.Item>
                  <Nav.Link eventKey="HTML">HTML</Nav.Link>
                </Nav.Item>
              </Nav>

              <Tab.Content className="col-md-12 col-sm-11 col-11 mt-2">
                <Tab.Pane eventKey="URL">
                  <div className="d-flex align-items-center justify-content-center border rounded ps-3 pt-3 px-3">
                    <div className="overflow-auto">
                      <p
                        className="font-monospace text-body-secondary"
                        style={{
                          wordWrap: "break-word",
                          textOverflow: "hidden",
                        }}
                      >
                        {badgeURI}
                      </p>
                    </div>
                    <div className="d-flex ms-auto pb-3">
                      <CopyToClipboard textToCopy={badgeURI} />
                    </div>
                  </div>
                </Tab.Pane>
                <Tab.Pane eventKey="Markdown">
                  <div className="d-flex align-items-center justify-content-center border rounded ps-3 pt-3 px-3">
                    <div className="overflow-auto">
                      <p
                        className="font-monospace text-body-secondary"
                        style={{
                          wordWrap: "break-word",
                          textOverflow: "hidden",
                        }}
                      >
                        ![Static Badge]({badgeURI})
                      </p>
                    </div>
                    <div className="d-flex ms-auto pb-3">
                      <CopyToClipboard
                        textToCopy={`![Static Badge](${badgeURI})`}
                      />
                    </div>
                  </div>
                </Tab.Pane>
                <Tab.Pane eventKey="rSt">
                  <div className="d-flex align-items-center justify-content-center border rounded ps-3 pt-3 px-3">
                    <div className="overflow-auto">
                      <p
                        className="font-monospace text-body-secondary"
                        style={{
                          wordWrap: "break-word",
                          textOverflow: "hidden",
                        }}
                      >
                        .. image:: ${badgeURI}
                        <br />
                        :alt: Static Badge
                      </p>
                    </div>
                    <div className="d-flex ms-auto pb-3">
                      <CopyToClipboard
                        textToCopy={`.. image:: ${badgeURI}
                      :alt: Static Badge
                   `}
                      />
                    </div>
                  </div>
                </Tab.Pane>
                <Tab.Pane eventKey="AsciiDoc">
                  <div className="d-flex align-items-center justify-content-center border rounded ps-3 pt-3 px-3">
                    <div className="overflow-auto">
                      <p
                        className="font-monospace text-body-secondary"
                        style={{
                          wordWrap: "break-word",
                          textOverflow: "hidden",
                        }}
                      >
                        image:${badgeURI}[Static Badge]
                      </p>
                    </div>
                    <div className="d-flex ms-auto pb-3">
                      <CopyToClipboard
                        textToCopy={`image:${badgeURI}[Static Badge]
                      `}
                      />
                    </div>
                  </div>
                </Tab.Pane>
                <Tab.Pane eventKey="HTML">
                  <div className="d-flex align-items-center justify-content-center border rounded ps-3 pt-3 px-3">
                    <div className="overflow-auto">
                      <p
                        className="font-monospace text-body-secondary"
                        style={{
                          wordWrap: "break-word",
                          textOverflow: "hidden",
                        }}
                      >
                        &lt;img alt=&quot;Static Badge&quot; src=&quot;
                        {badgeURI}
                        &quot;/&gt;
                      </p>
                    </div>
                    <div className="d-flex ms-auto pb-3">
                      <CopyToClipboard
                        textToCopy={`<img alt="Static Badge" src="${badgeURI}"/>
                      `}
                      />
                    </div>
                  </div>
                </Tab.Pane>
              </Tab.Content>
            </Tab.Container>
          </div>
        </Accordion.Body>
      </Accordion.Item>
    </Accordion>
  );
};

export default EmbedBadges;
