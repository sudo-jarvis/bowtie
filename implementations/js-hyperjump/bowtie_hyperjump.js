import readline from "readline/promises";
import os from "os";
import process from "process";
import {
  registerSchema,
  unregisterSchema,
  validate,
} from "@hyperjump/json-schema/draft-2020-12";
import "@hyperjump/json-schema/draft-2019-09";
import "@hyperjump/json-schema/draft-07";
import "@hyperjump/json-schema/draft-06";
import "@hyperjump/json-schema/draft-04";
import packageJson from "./node_modules/@hyperjump/json-schema/package.json" assert { type: "json" };

const hyperjump_version = packageJson.version;

const stdio = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false,
});

function send(data) {
  console.log(JSON.stringify(data));
}

var started = false;
var dialect = null;

// Skip
const keywordsNotInSchemaMessage =
  "Ignoring schema meta-data keywords in places that are not schemas (such as a $id in a const) is not supported. Because this implementation is dialect agnostic, there's no way to know whether a location is a schema or not. Especially because there's no reason for a schema to use keywords in places that aren't schemas, I'm not concerned about making it work.";
const keywordsNotInSchemaSkippedTests = [
  "naive replacement of $ref with its destination is not correct",
  "$ref prevents a sibling id from changing the base uri",
  "$ref prevents a sibling $id from changing the base uri",
].reduce((acc, description) => {
  acc[description] = keywordsNotInSchemaMessage;
  return acc;
}, {});

const boundaryCrossingMessage =
  "JSON pointers that cross schema resource boundaries are not suppported. There might be a way to solve this, but because this functionality has been removed from the spec and there is no good reason to do this in any version of the spec, it will probably never be fixed.";
const boundaryCrossingSkippedTests = {
  "base URI change - change folder in subschema": boundaryCrossingMessage,
};

const fileSchemeMessage =
  "Self-identifying with a `file:` URI is not allowed for security reasons.";
const fileSchemeSkippedTests = {
  "id with file URI still resolves pointers - *nix": fileSchemeMessage,
  "id with file URI still resolves pointers - windows": fileSchemeMessage,
  "$id with file URI still resolves pointers - *nix": fileSchemeMessage,
  "$id with file URI still resolves pointers - windows": fileSchemeMessage,
};

const modernSkippedTests = { ...fileSchemeSkippedTests };
const legacySkippedTests = {
  ...boundaryCrossingSkippedTests,
  ...keywordsNotInSchemaSkippedTests,
  ...fileSchemeSkippedTests,
};

const dialectSkippedTests = {
  "https://json-schema.org/draft/2020-12/schema": modernSkippedTests,
  "https://json-schema.org/draft/2019-09/schema": modernSkippedTests,
  "http://json-schema.org/draft-07/schema#": legacySkippedTests,
  "http://json-schema.org/draft-06/schema#": legacySkippedTests,
  "http://json-schema.org/draft-04/schema#": legacySkippedTests,
};

const cmds = {
  start: async (args) => {
    console.assert(args.version === 1, { args });
    started = true;
    return {
      version: 1,
      implementation: {
        language: "javascript",
        name: "hyperjump-json-schema",
        version: hyperjump_version,
        homepage: "https://json-schema.hyperjump.io/",
        issues: "https://github.com/hyperjump-io/json-schema/issues",
        source: "https://github.com/hyperjump-io/json-schema",

        dialects: [
          "https://json-schema.org/draft/2020-12/schema",
          "https://json-schema.org/draft/2019-09/schema",
          "http://json-schema.org/draft-07/schema#",
          "http://json-schema.org/draft-06/schema#",
          "http://json-schema.org/draft-04/schema#",
        ],
        os: os.platform(),
        os_version: os.release(),
        language_version: process.version,
      },
    };
  },

  dialect: async (args) => {
    console.assert(started, "Not started!");
    dialect = args.dialect;
    return { ok: true };
  },

  run: async (args) => {
    console.assert(started, "Not started!");

    const testCase = args.case;

    let results;
    if (testCase.description in dialectSkippedTests[dialect]) {
      results = testCase.tests.map((_) => {
        return {
          skipped: true,
          message: dialectSkippedTests[dialect][testCase.description],
        };
      });
    } else {
      const retrievalUri = `https://example.com/bowtie-sent-schema-${args.seq.toString()}`;

      try {
        for (const id in testCase.registry) {
          const schema = testCase.registry[id];
          if (!schema.$schema || schema.$schema === dialect) {
            registerSchema(schema, id, dialect);
          }
        }

        registerSchema(testCase.schema, retrievalUri, dialect);

        const _validate = await validate(retrievalUri);
        results = testCase.tests.map((test) => {
          try {
            const result = _validate(test.instance);
            return { valid: result.valid };
          } catch (error) {
            return { errored: true, context: { message: error.message } };
          }
        });
      } catch (error) {
        results = testCase.tests.map((_) => ({
          errored: true,
          context: { message: error.message },
        }));
      } finally {
        unregisterSchema(retrievalUri);

        for (const id in testCase.registry) {
          unregisterSchema(id);
        }
      }
    }

    return { seq: args.seq, results: results };
  },

  stop: async (_) => {
    console.assert(started, "Not started!");
    process.exit(0);
  },
};

async function main() {
  for await (const line of stdio) {
    const request = JSON.parse(line);
    const response = await cmds[request.cmd](request);
    send(response);
  }
}

main();
