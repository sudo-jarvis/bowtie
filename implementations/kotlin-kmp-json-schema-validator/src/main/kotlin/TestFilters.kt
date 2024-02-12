import io.github.optimumcode.json.schema.SchemaType

interface TestFilter {
    /**
     * @return reason if test case should be skipped
     */
    fun shouldSkipCase(caseDescription: String): String? = null

    /**
     * @return reason if test in test case should be skipped
     */
    fun shouldSkipTest(caseDescription: String, testDescription: String): String? = null
}

fun getFilter(schemaType: SchemaType?): TestFilter =
    when (schemaType ?: SchemaType.entries.last()) {
        SchemaType.DRAFT_7 -> TestFilterDraft7
        SchemaType.DRAFT_2019_09 -> TestFilterDraft201909
        SchemaType.DRAFT_2020_12 -> TestFilterDraft202012
    }

object TestFilterDraft7 : TestFilter {

    override fun shouldSkipCase(caseDescription: String): String? {
        return when {
            caseDescription.endsWith(" format") -> "the format keyword is not yet supported"
            else -> null
        }
    }
}

object TestFilterDraft201909 : TestFilter {
    private val IGNORED_CASES_WITH_CUSTOM_META_SCHEMA: Set<String> = hashSetOf(
        "schema that uses custom metaschema with with no validation vocabulary",
        "ignore unrecognized optional vocabulary",
    )

    private val IGNORE_CASES_WITH_MIN_CONTAINS_ZERO = setOf(
        "minContains = 0 with no maxContains",
    )

    override fun shouldSkipCase(caseDescription: String): String? {
        return when {
            caseDescription.endsWith(" format") -> "the format keyword is not yet supported"
            caseDescription in IGNORED_CASES_WITH_CUSTOM_META_SCHEMA ->
                "vocabulary from custom meta-schemas is not supported yet"
            caseDescription in IGNORE_CASES_WITH_MIN_CONTAINS_ZERO ->
                "'minContains' does not affect contains work - at least one element must match 'contains' schema"
            else -> null
        }
    }

    override fun shouldSkipTest(caseDescription: String, testDescription: String): String? {
        return when {
            caseDescription == "minContains = 0 with maxContains" &&
                testDescription == "empty data" ->
                "'minContains' does not affect contains work -" +
                    " at least one element must match 'contains' schema"
            else -> null
        }
    }
}

object TestFilterDraft202012 : TestFilter {
    private val IGNORED_CASES_WITH_CUSTOM_META_SCHEMA: Set<String> = hashSetOf(
        "schema that uses custom metaschema with with no validation vocabulary",
        "ignore unrecognized optional vocabulary",
    )

    override fun shouldSkipCase(caseDescription: String): String? {
        return when {
            caseDescription.endsWith(" format") -> "the format keyword is not yet supported"
            caseDescription in IGNORED_CASES_WITH_CUSTOM_META_SCHEMA ->
                "vocabulary from custom meta-schemas is not supported yet"
            else -> null
        }
    }
}
