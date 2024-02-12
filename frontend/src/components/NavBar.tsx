import { useContext, useEffect } from "react";
import { Sun, MoonStarsFill } from "react-bootstrap-icons";
import { Link, NavLink, useLocation, useMatch } from "react-router-dom";

import { ThemeContext } from "../context/ThemeContext";
import { BowtieVersionContext } from "../context/BowtieVersionContext";
import logo from "../assets/landscape-logo.svg";
import Dialect from "../data/Dialect";

const NavBar = () => {
  const { isDarkMode, toggleDarkMode } = useContext(ThemeContext);
  const { version } = useContext(BowtieVersionContext);
  const { hash, key } = useLocation();

  const rootMatch = useMatch("/");
  const dialectsMatch = useMatch("/dialects/*");
  const isDialectPage = rootMatch ?? dialectsMatch;

  useEffect(() => {
    if (hash) {
      const targetElement = document.getElementById(hash.substring(1));
      targetElement?.scrollIntoView({ behavior: "smooth" });
    }
  }, [key, hash]);

  return (
    <>
      <nav
        className={`navbar navbar-expand-lg sticky-top mb-4 ${
          isDarkMode ? "navbar-dark bg-dark" : "navbar-light bg-light"
        }`}
      >
        <div className="container-fluid">
          <Link className="navbar-brand me-4 py-1" to="/">
            <img src={logo} alt="Bowtie" width="128px" />
          </Link>
          <button
            className="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarNav"
            aria-controls="navbarSupportedContent"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav me-auto mb-2 mb-lg-0">
              {isDialectPage && (
                <>
                  <li className="nav-item">
                    <Link className="nav-link" to={{ hash: "run-info" }}>
                      Run Info
                    </Link>
                  </li>
                  <li className="nav-item">
                    <Link className="nav-link" to={{ hash: "summary" }}>
                      Summary
                    </Link>
                  </li>
                  <li className="nav-item">
                    <Link className="nav-link" to={{ hash: "cases" }}>
                      Details
                    </Link>
                  </li>
                </>
              )}
              <li className="nav-item dropdown">
                <a
                  className="nav-link dropdown-toggle"
                  role="button"
                  data-bs-toggle="dropdown"
                  aria-expanded="false"
                >
                  Dialects{" "}
                </a>
                <ul className="dropdown-menu">
                  {Dialect.newest_to_oldest().map((dialect) => (
                    <li key={dialect.path}>
                      <NavLink
                        className="dropdown-item"
                        to={`/dialects/${dialect.path}`}
                      >
                        {dialect.prettyName}
                      </NavLink>
                    </li>
                  ))}
                  <li>
                    <NavLink className="dropdown-item" to="/local-report/">
                      Local report
                    </NavLink>
                  </li>
                </ul>
              </li>
            </ul>
          </div>
          <button id="docs" className="btn btn-sm btn-secondary border-0 me-1">
            <Link
              className="nav-link"
              to="https://docs.bowtie.report/"
              target="blank"
            >
              Docs
            </Link>
          </button>
          <button
            id="theme-toggler"
            className="btn border-0 me-1"
            onClick={() => toggleDarkMode!()}
          >
            {isDarkMode ? <MoonStarsFill size={20} /> : <Sun size={20} />}
          </button>
          <a
            href="https://github.com/bowtie-json-schema/bowtie/"
            className="link-secondary"
          >
            <span className="navbar-text">
              {version && <small>Bowtie v{version}</small>}
            </span>
          </a>
        </div>
      </nav>
    </>
  );
};

export default NavBar;
