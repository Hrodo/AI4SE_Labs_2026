# PINES Management Processes — Consolidated Reporting & Tools Requirements (Final Draft)

Requirements for management reporting, analysis, and collection/asset-management utilities used by PINES library managers, administrators, and staff. This covers reporting features, query tools and templates, item transfer and purging utilities, deletion/audit logging, patron-demographic and inactivity reporting, reporting infrastructure (performance, queueing, scheduling, historical data), platform and security constraints, documentation and help, and related operational processes. It explicitly excludes day-to-day patron-facing OPAC and circulation client functional requirements except where those systems are a required data source.

Review status: **needs_review**. Refinement passes: 3.

## Priority scale

- **Must**: Explicitly mandatory, essential to the agreed scope, or marked high priority.
- **Should**: Important but not explicitly mandatory; the default when priority is unstated.
- **Could**: Optional, desirable, or explicitly low priority.

## Glossary

- OPAC: Online Public Access Catalog (public-facing catalog interface).
- Report template / canned report: A pre-configured query and display format that staff may run or modify subject to permissions.
- Data warehouse / reporting warehouse: A copy or aggregation layer of production data optimized for historical reporting and snapshot queries.
- Pull list / transit label: Printed output to assist physical movement of items (barcodes, destination, etc.).
- Reversion / auto-revert: Automatic process that returns an item's location (or location field) to a previous value after a configured condition or time interval.
- Snapshot report: A saved (time-stamped) result set for historical comparison that does not change when live data changes.
- Last copy report: Report identifying bibliographic records for which a system or branch holds the last known copy.
- Denormalized schema: A database schema arranged to speed reporting at the cost of duplication; discouraged unless specifically justified.

## Requirements

### REQ-0001: Material Volume Reporting

The system shall provide reports showing the volume of material in the library at a given point in time and over time. Reports shall include counts of new acquisitions, items on shelf (checked in), and items out in circulation. Reports shall allow breaking down volume by categories (for example: total items, number of holds, adult fiction, board books) and shall support customizable categories and historical/time-based summaries.

Priority: **Must**. Explicit request and central management need for collection volume and categorization; core management process requirement.

Sources: `conversations/conv_pines014_material_volume.eml`, `interview_cataloging_2009-05-08.txt`.

Evidence candidates: C-00001, C-00122.

### REQ-0002: Branch Capacity Overview and Drill-Down

The system shall provide a high-level summary (dashboard) view that displays capacity metrics for all branches simultaneously. Users shall be able to drill down from the multi-branch overview to detailed capacity information for an individual branch. The dashboard shall support sorting and filtering (e.g., by region, library type, current load) and display trends indicating whether branches are growing or shrinking over time to aid long-term planning.

Priority: **Must**. Explicitly requested as a core executive/managerial view and referenced as 'must' for decision making.

Sources: `conversations/conv_pines015_capacity_interface.eml`.

Evidence candidates: C-00002, C-00003, C-00004, C-00005.

### REQ-0003: Shelf Space Utilization and Comparative Reporting

The system shall provide a shelf-space report that, for each genre and format, computes and compares: percentage of total circulations, percentage of the collection, and percentage of total shelf space. The report shall be runnable per library and at the system level, allow side-by-side comparisons across libraries (comparison view), and support date-range filtering to compare quarters or seasons. Because shelf space is not directly tracked, the system shall provide an estimation method (see separate requirement) and document estimation assumptions in the report output.

Priority: **Must**. Multiple stakeholders requested this report for collection management and system comparison; functionality is specifically described and required.

Sources: `conversations/conv_pines016_shelf_space.eml`, `interview_cataloging_2009-05-08.txt`.

Evidence candidates: C-00007, C-00008, C-00009, C-00010, C-00011, C-00012, C-00121.

### REQ-0004: Shelf Space Estimation Investigations

Because shelf space is not tracked directly, the project shall investigate and document methods to estimate shelf space from existing data (for example, using item dimensions if available, or using item count as a proxy). The selected estimation approach and its limitations shall be recorded and surfaced in the shelf-space report so users understand assumptions and accuracy.

Priority: **Should**. Estimation is necessary for the shelf-space report to be usable, but approaches may vary; investigation and documented method are required though choice of algorithm is implementation detail.

Sources: `conversations/conv_pines014_material_volume.eml`, `conversations/conv_pines016_shelf_space.eml`.

Evidence candidates: C-00008, C-00012, C-00169.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0005: Export and Report Output Formats (CSV/Pivot/Fields)

The system shall allow exporting reports and report results in common formats such as CSV for spreadsheet use, and support pivot-table-ready output. Reports shall be able to include multiple output columns (e.g., last month's circulation, previous month's circulation, percent differences, previous year's month) and be able to include MARC fields or other bibliographic fields so that relevant bibliographic data can appear on a single row per result when requested.

Priority: **Must**. Export to CSV and flexible output columns are repeatedly requested for directors and staff who work with spreadsheets; fundamental for interoperability.

Sources: `conversations/conv_pines015_capacity_interface.eml`, `conversations/conv_pines024_inactive_patrons.eml`, `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`.

Evidence candidates: C-00006, C-00051, C-00079, C-00069, C-00088, C-00080, C-00108.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0006: Shelf / Transfer Physical Handling Outputs (Pull Lists & Labels)

When items are selected for transfer or movement, the system shall be able to produce printable pull lists and transit labels that include barcodes and destination information to streamline physical handling and tracking. Pull lists shall be printable and exportable for staff workflows.

Priority: **Must**. Physical handling of transferred items requires printed lists/labels to operationalize transfers.

Sources: `conversations/conv_pines018_item_transfer.eml`, `survey_results_2009.txt`.

Evidence candidates: C-00017, C-00246.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0007: Item Transfer / Branch Transfer Utility

The system shall provide a transfer utility supporting: a query builder to select candidate items for transfer (with ability to save/share queries as templates), manual selection (checkboxes) from query results, changing selected items' location fields (batch update) or producing pull lists for physical transfer, and a mechanism to revert items to their original location (automatic or manual) after a configured period or upon certain events. The utility shall have permissions restricting who may perform transfers and must support preview and confirmation before changes, an undo/rollback mechanism, notifications for transfer delays or issues, and logging of transfer activities for audit purposes.

Priority: **Must**. Staff operational need for predictable, repeatable transfers and safeguards (preview, undo, permissions) is strongly emphasized; transfers affect large numbers of items and must be controlled.

Sources: `conversations/conv_pines018_item_transfer.eml`, `interview_cataloging_2009-05-08.txt`, `survey_results_2009.txt`.

Evidence candidates: C-00013, C-00014, C-00015, C-00016, C-00017, C-00018, C-00019, C-00020, C-00021, C-00022, C-00023, C-00024, C-00025, C-00026, C-00115, C-00242, C-00246.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0008: Auto-Revert and Scheduled Reversion Processing

The system shall support automatic reversion of transferred items to their original location based on elapsed time (configurable, e.g., 30 days) and/or event triggers (e.g., status change to 'sold', item checked out at destination). A background scheduled task shall periodically evaluate transferred items and perform reversion or flag items for review according to configured criteria.

Priority: **Should**. Auto-revert automates maintenance but policies and exact triggers need local configuration; listed as important but implementation details configurable.

Sources: `conversations/conv_pines014_material_volume.eml`, `conversations/conv_pines018_item_transfer.eml`, `survey_results_2009.txt`.

Evidence candidates: C-00018, C-00019, C-00020, C-00170, C-00243, C-00244.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0009: Transfer Activity Logging and Item Transfer History

All transfer-related activities (batch updates, manual transfers, reverts, pull-list generation, and notifications) shall be logged. The system shall allow viewing the transfer history for an individual item (for example, number of transfers in the past year) to identify circulation or location issues.

Priority: **Must**. Operational traceability and auditing are essential for trustworthy inventory operations and to diagnose transfer-related problems.

Sources: `conversations/conv_pines018_item_transfer.eml`, `survey_results_2009.txt`.

Evidence candidates: C-00021, C-00026, C-00242, C-00246.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0010: Permissions and Role Restrictions for Transfer & Report Actions

The system shall restrict transfer, purge, and other data-modifying functions to authorized roles (e.g., managers, administrators, transfer coordinators). Permissions shall be manageable via roles and security groups so that altering a user's role updates their permissions automatically.

Priority: **Must**. Prevents unauthorized or accidental data modifications; explicitly requested.

Sources: `conversations/conv_pines018_item_transfer.eml`, `early_draft_srs_galecia.txt`, `email_report_features.eml`, `email_staff_login.eml`, `evergreen_reference_2009.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `survey_results_2009.txt`.

Evidence candidates: C-00022, C-00060, C-00094, C-00102, C-00103, C-00104, C-00130, C-00150, C-00112, C-00247.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0011: Missing, Damaged, and In-Transit Items Reporting

The system shall generate reports listing missing and damaged items, segmented by branch. The system shall also provide an in-transit items report that lists items in transit beyond a configurable number of days (default configurable; a suggested default is 7 days), merging outbound and inbound transit records into one view, and support sorting (for example by due date) to prioritize action.

Priority: **Must**. Regular shelf-reading and transit monitoring require actionable reports; repeatedly requested by cataloging and operations staff.

Sources: `conversations/conv_pines019_020_missing_intransit.eml`, `interview_cataloging_2009-05-08.txt`.

Evidence candidates: C-00027, C-00028, C-00116, C-00117.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0012: Item Purging / Weeding Utility and Safety Controls

The system shall provide a utility and reports to identify candidate item records for purging using configurable combined criteria (e.g., status='missing' for > X months, status='discard/weed', circulation inactivity). Workflows shall include read-only candidate reports, a separate confirmation step before deletion, last-copy reports to avoid deleting sole copies, and an audit trail of purge actions. There shall also be tools for deleting volume entries along with their copies and cleaning records with no attached items.

Priority: **Must**. Data removal is sensitive and requires safe workflows and auditability; explicitly requested by cataloging and operations staff.

Sources: `conversations/conv_pines021_item_purging.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`, `meeting_tech_subcommittee_2009-06-30.txt`.

Evidence candidates: C-00029, C-00118, C-00119, C-00070, C-00241.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0013: Deletion Audit Logging and Deletion Report Interface

The system shall log deletions (records removed) to an audit table capturing at a minimum: record_type, record_id, deleted_by, deleted_at (timestamp), and location. The system shall provide a report interface to query the audit table and allow filtering by date range, user, record type, location, and system. The system shall also count deletions by period (monthly/quarterly/yearly) and by record type and location, and shall log attempted/denied deletions for security monitoring. The capability to list deleted items that were last copies (for updating external catalogs such as WorldCat) shall be supported.

Priority: **Must**. Deletion logging does not exist in current system and is necessary for auditability, compliance, and troubleshooting; explicitly requested.

Sources: `conversations/conv_pines022_deletions.eml`, `early_draft_srs_galecia.txt`, `email_report_features.eml`, `interview_cataloging_2009-05-08.txt`, `interview_sysadmin_2009-05-10.txt`.

Evidence candidates: C-00030, C-00031, C-00032, C-00033, C-00034, C-00035, C-00036, C-00120, C-00073, C-00087, C-00233, C-00210, C-00186, C-00120.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0014: Query Builder and Report Designer UI

The system shall provide a user-friendly query-builder interface for designing complex queries across all record types. Features shall include selecting fields, picklist value selection, regular-expression support, Boolean operators, visible display of query criteria alongside results, and the ability to save/share queries and create report templates that administrators can make available to staff (runnable as-is or editable within admin-defined constraints). Templates shall be clonable to create variants.

Priority: **Must**. Core functionality for staff to define ad-hoc and recurring reports; consistently emphasized across stakeholders.

Sources: `conversations/conv_pines018_item_transfer.eml`, `early_draft_srs_galecia.txt`, `email_report_features.eml`, `meeting_minutes/meeting_2009-03-15_minutes.txt`, `survey_results_2009.txt`.

Evidence candidates: C-00091, C-00097, C-00092, C-00093, C-00071, C-00072, C-00068, C-00014, C-00165, C-00137, C-00136, C-00201, C-00202.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0015: Report Templates, Shared Folders and Fine-Grained Report Permissions

The system shall support administrator-created report templates, shared folders for report access control, and fine-grained permissions to control who may create, clone, edit, run, schedule, or distribute reports. Permissions shall reflect role changes dynamically and support folders or collections of templates with controlled editability. Administrators shall be able to limit which filters and display fields staff may alter.

Priority: **Must**. Consistency and security in reporting across the consortium require template management and permission controls; explicit user requests and surveys indicate this as necessary.

Sources: `early_draft_srs_galecia.txt`, `email_report_features.eml`, `survey_results_2009.txt`.

Evidence candidates: C-00094, C-00165, C-00166, C-00167, C-00072, C-00071, C-00093.

### REQ-0016: Report Scheduling, Queue Management, Prioritization and Cancellation

The system shall provide a queuing mechanism for report processing, show users their report position in the queue (number of reports ahead, submission time, current status such as waiting/running/completed/failed), allow cancelling scheduled or running reports, and allow prioritization/escalation of reports (for example, giving board reports priority over ad-hoc staff reports). The system shall permit scheduling frequencies including Run ASAP, Hourly, Daily, Weekly, Monthly, Yearly and support email delivery and address-book based distribution.

Priority: **Must**. Operationally necessary to manage heavy reporting load and to ensure critical reports are delivered timely; explicitly requested.

Sources: `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `survey_results_2009.txt`.

Evidence candidates: C-00098, C-00099, C-00074, C-00081, C-00107, C-00168, C-00203.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0017: Historical Reporting and Data Warehouse Support

The system shall support historical reporting via a reporting warehouse or snapshot capability that allows acquiring data as-of a given date or date range and generating snapshot reports for longitudinal analysis. Transaction history retention shall be configurable (X days), while monthly and annual aggregates shall be retained indefinitely if configured. The reporting architecture shall avoid denormalized schemas that cause sync issues unless a justified ETL approach is chosen.

Priority: **Should**. Historical analysis is valuable for planning and required by some users; implementation may require architectural work so priority is 'Should' where not explicitly called 'must' though many stakeholders requested it.

Sources: `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `meeting_tech_subcommittee_2009-06-30.txt`, `survey_results_2009.txt`.

Evidence candidates: C-00084, C-00083, C-00109, C-00113, C-00156, C-00157, C-00213, C-00204.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0018: Background Processing, Read-Only Reporting Replicas and Performance

To avoid disrupting live circulation and OPAC performance during open hours, the system shall support running long queries and reports as background jobs, caching results, using queuing, and/or using read-only reporting replicas. The system shall scale to support a large consortium (for example, 286 locations, ~17M annual circulations, and ~900k items/year processed) without adversely affecting online patrons and staff operations.

Priority: **Must**. Large-consortium scale and explicit reports of current system contention make background processing/read-only replicas essential for operational viability.

Sources: `conversations/conv_pines024_inactive_patrons.eml`, `email_report_features.eml`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`.

Evidence candidates: C-00052, C-00126, C-00142, C-00125, C-00129, C-00132, C-00218, C-00131.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0019: Server Platform, Browser and Accessibility Requirements

Management Processes shall operate on Linux or Solaris server environments. If web-browser access is used, the system shall be accessible through Microsoft Internet Explorer (v6.0 and later) and Mozilla Firefox (v2.0 and later). The system shall produce standards-compliant HTML and support assistive technologies (screen-reading, screen-magnification), complying with accessibility requirements (e.g., Section 508).

Priority: **Must**. Explicit platform & accessibility constraints were stated as high priority and/or legal/regulatory requirements.

Sources: `conversations/conv_pines016_shelf_space.eml`, `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`.

Evidence candidates: C-00054, C-00055, C-00056, C-00057, C-00058, C-00059, C-00143, C-00144, C-00145, C-00146, C-00147, C-00148, C-00125, C-00127, C-00128, C-00111, C-00177.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0020: Authentication Options and Individual Auditability

The system shall support multiple staff login methods including streamlined local login (e.g., card-swipe) and traditional username/password. Streamlined login shall still identify the specific staff member for audit purposes, and role-based access control shall be used so that changing a user's role updates their permissions automatically.

Priority: **Should**. Multiple login options aid usability; individual auditability is essential but the streamlined option can be optional per site.

Sources: `email_staff_login.eml`, `meeting_minutes/meeting_2009-03-15_minutes.txt`.

Evidence candidates: C-00100, C-00101, C-00102, C-00104, C-00236.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0021: Help System and Error Reporting

The system shall provide an integrated online help system in HTML that is hierarchical, cross-linked, searchable, and illustrates all major functions. The system shall also provide high-level error reporting and low-level query-specific feedback for administrators to support troubleshooting.

Priority: **Must**. Users require integrated help and administrators require diagnostics for effective operation; marked High Priority in source material.

Sources: `conversations/conv_pines016_shelf_space.eml`, `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `survey_results_2009.txt`.

Evidence candidates: C-00063, C-00064, C-00154, C-00155, C-00133, C-00248, C-00180, C-00224, C-00212, C-00133.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0022: Data Specification and Major Process Documentation

The developer shall provide complete data specifications for authority, bibliographic, order, item, hold/request, and other records used by Management Processes. The developer shall also provide high-level descriptions of major processes (e.g., bibliographic import/export, validation, reporting processes) so staff and developers understand data structures and flows used by reports.

Priority: **Must**. Report authors, administrators, and integrators require accurate data specification and process descriptions to build and validate reports.

Sources: `early_draft_srs_galecia.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`.

Evidence candidates: C-00061, C-00062, C-00152, C-00153, C-00241.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0023: Transaction-level Reporting and Counting

The system shall support transaction reporting grouped by hour, terminal, branch, and system. It shall count separately and cumulatively all check-in and check-out types (e.g., book-drop, staff, self-checkout, renewals via staff and OPAC). Holds reporting shall include method of placement (staff desk, public computer, remote), and transaction reports shall support per-patron, per-library, per-group-of-libraries, per-system, and per-county rollups. Reports shall include total circulations broken down by checkouts, renewals, and non-cataloged uses where applicable.

Priority: **Must**. Detailed transaction accounting and breakdowns are core reporting needs described repeatedly in source material.

Sources: `early_draft_srs_galecia.txt`, `email_financial_reports.eml`, `email_report_features.eml`, `survey_results_2009.txt`.

Evidence candidates: C-00157, C-00158, C-00159, C-00160, C-00161, C-00162, C-00075, C-00076, C-00078, C-00164, C-00163, C-00215, C-00208, C-00206, C-00207.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0024: Patron Demographics, Filtering, Grouping and Inactive Patron Reports

The system shall support filtering (LIMIT) and grouping (GROUP BY) of patron records by characteristics such as zip code, county, home branch, patron type, preferred language, and effective age range. Age ranges shall be computed at query time from birth_date and be configurable. Filters shall be combinable with AND/OR logic, and reports shall include null/missing values rather than silently excluding them. Inactivity reports shall allow a configurable inactivity threshold (X days, default commonly 365), include electronic activity (OPAC logins, online holds, renewals, digital access where logged) by combining events across tables, support excluding certain patrons (do-not-disturb, VIPs, staff, opted-out patrons), include current mailing addresses for outreach, support export (e.g., CSV), and be runnable at multiple organizational levels (system, home library, county). For very large patron datasets, inactivity reporting shall be performed as background jobs with cached results.

Priority: **Must**. Patron segmentation and inactivity workflows are operational necessities and appear in multiple sources; performance concerns require background processing.

Sources: `conversations/conv_pines023_patron_characteristics.eml`, `conversations/conv_pines024_inactive_patrons.eml`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`.

Evidence candidates: C-00037, C-00038, C-00039, C-00040, C-00041, C-00042, C-00043, C-00044, C-00045, C-00046, C-00047, C-00048, C-00049, C-00050, C-00051, C-00052, C-00053, C-00234, C-00235, C-00239, C-00240.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0025: Report Metadata, Selection Criteria and Inclusion of Nulls

Each report shall clearly define and display its selection criteria and the date range applied. Reports shall include nulls and blank fields in result sets rather than silently excluding them so analysts are aware of missing data.

Priority: **Must**. Clarity of report parameters and inclusion of nulls is needed to avoid misleading analyses; explicitly requested.

Sources: `early_draft_srs_galecia.txt`.

Evidence candidates: C-00085, C-00082, C-00204, C-00200.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0026: Valuation and Financial-style Item Reports

The system shall provide reports that compute the monetary value of items based on data in item records (value of entire collection or subsets, e.g., all items with status 'longoverdue', or all DVDs in children's collection). Reports shall be filterable by status and media type and comply with accounting/audit requirements.

Priority: **Should**. Valuation reports are important for financial and insurance needs but are less frequently requested than operational reports; still required and must comply with auditing standards.

Sources: `email_financial_reports.eml`, `email_report_features.eml`.

Evidence candidates: C-00090, C-00205, C-00206, C-00216.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0027: Data Quality, Inventory and Uncataloged Material Tracking

The system shall include data-quality reports to identify inconsistencies such as invalid item types, bibliographic records with no items, long call numbers, and other anomalies. The system shall support tracking uncataloged material (e.g., large shipments of paperbacks or children's books) to enable quick distribution with minimal branch labor and to monitor usage and circulation of uncataloged items. Reports shall show last edit dates where items were explicitly modified (not last circulation date) when that information is available.

Priority: **Should**. Data quality and uncataloged-material tracking are important for operations and efficiency; prioritized but some sites may treat as lower immediate priority than core reporting.

Sources: `interview_cataloging_2009-05-08.txt`, `meeting_tech_subcommittee_2009-06-30.txt`.

Evidence candidates: C-00123, C-00114, C-00124, C-00241.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0028: Pull MARC Fields, Last-Copy and Deleted Items Reporting for External Catalogs

The system shall be able to include MARC record fields in report rows and produce reports identifying items deleted that were last copies held by the facility to support updates to external catalogs (e.g., WorldCat).

Priority: **Must**. Maintaining bibliographic data in external systems and producing single-row MARC outputs are explicit operational needs.

Sources: `early_draft_srs_galecia.txt`, `interview_sysadmin_2009-05-10.txt`.

Evidence candidates: C-00073, C-00088, C-00087, C-00233.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0029: Report Development Process, Prototyping, and Working Group Responsibilities

The Reports Working Group shall document the desired reporting functionality, collect requirements via interviews, adopt/adapt existing SRS materials (e.g., Galecia King County SRS) as a foundation, and serve as the designated testing group for new reports development. UI specifics will be developed iteratively using prototypes, with an emphasis on readable documentation for technical and non-technical stakeholders.

Priority: **Should**. Process and governance are necessary for high-quality outcomes; implementation is organizational rather than technical.

Sources: `evergreen_reference_2009.txt`, `meeting_minutes/meeting_2009-03-15_minutes.txt`.

Evidence candidates: C-00134, C-00135, C-00136, C-00137, C-00138, C-00140, C-00141, C-00225, C-00226, C-00227, C-00228, C-00229, C-00230, C-00231, C-00232.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0030: Scope: Management Processes Only (Separation from OPAC/Circulation Features)

The requirements in this specification shall be scoped to Management Processes (reports and analysis tools used by managers, administrators, and staff for planning, evaluation and oversight). They shall not be used to constrain the OPAC or circulation client functionality. The management reporting system shall integrate with OPAC/circulation data sources but remain operationally independent so that reporting activity does not degrade patron-facing modules.

Priority: **Must**. Explicit scope decision by stakeholders; necessary to preserve module independence and performance.

Sources: `conversations/conv_pines016_shelf_space.eml`, `conversations/conv_pines024_inactive_patrons.eml`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-03-15_minutes.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`.

Evidence candidates: C-00135, C-00139, C-00151, C-00211, C-00223, C-00132, C-00179, C-00197.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0031: Development / Training Environments and Configuration Migration

The system shall provide separate development/training environments where reports and configurations may be developed and tested without affecting production. There shall be a mechanism to migrate report templates, permission settings, and other configurations from development/training to production.

Priority: **Should**. Separation of environments is important for safe development; stated in subcommittee and admin feedback as required but may be implemented after core features.

Sources: `evergreen_reference_2009.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-03-15_minutes.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`.

Evidence candidates: C-00131, C-00149, C-00110, C-00238.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0032: Report Queue Visibility and Management for Users

Users shall be able to view the status of their reports in the queue (position, status, submission time, estimated completion) and be able to cancel their scheduled or running reports. The system shall provide administrative controls to prioritize or escalate reports as required.

Priority: **Must**. Operational transparency and control are necessary to manage heavy load and to provide predictable service levels.

Sources: `conversations/conv_pines019_020_missing_intransit.eml`, `conversations/conv_pines024_inactive_patrons.eml`, `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `survey_results_2009.txt`.

Evidence candidates: C-00168, C-00098, C-00099, C-00106, C-00184, C-00193, C-00203.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0033: Queue Prioritization Mechanism & Policy

The system shall provide mechanisms to prioritize certain classes of reports (for example, board reports) so they may jump ahead of resource-consuming ad-hoc queries. The system shall support administrative controls and an auditable prioritization policy. Policy details (limits, quotas, and escalation rules) shall be defined by stakeholders and captured as configuration.

Priority: **Must**. Operational need to ensure critical reports are delivered timely and to manage resource contention.

Sources: `conversations/conv_pines022_deletions.eml`, `early_draft_srs_galecia.txt`, `email_report_features.eml`, `survey_results_2009.txt`.

Evidence candidates: C-00074, C-00099, C-00168, C-00203, C-00187.

**Evidence warning:** At least one candidate has no verified quotation. Review this requirement against its source documents.

### REQ-0034: Report Output Quality and Proven Correctness

All report outputs shall be tested and proven correct. The system shall include testable output validation and provide provenance metadata (selection criteria, query used, run time) alongside report results to support verification and reproducibility.

Priority: **Must**. Trusted reporting requires reliable outputs and verification procedures; repeatedly requested.

Sources: `early_draft_srs_galecia.txt`, `email_report_features.eml`.

Evidence candidates: C-00080, C-00097, C-00201.

### REQ-0035: Scheduling, Delivery and Distribution Features

The system shall support scheduling reports at granular frequencies (Run ASAP, Hourly, Daily, Weekly, Monthly, Yearly), shall support email delivery and address-book based report distribution, and shall allow editing recurring reports (changing selections and recipient addresses).

Priority: **Must**. Operationally needed for recurring reporting and distribution to stakeholders.

Sources: `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`.

Evidence candidates: C-00107, C-00068, C-00081, C-00074, C-00099.

### REQ-0036: Pivot and Advanced Output Formats

Reports shall support output formats suitable for pivoting and further analysis (pivot table export), and the system shall support common formats such as CSV, and optionally Excel/PDF per stakeholder needs.

Priority: **Should**. Pivot-ready output and additional formats are highly useful; CSV is required and others are desirable based on stakeholder preference.

Sources: `early_draft_srs_galecia.txt`, `email_financial_reports.eml`.

Evidence candidates: C-00079, C-00069, C-00205.

## Blacklist

### BL-0001: Unassigned / Clarification Required Candidates

These candidates were present in the supplied corpus but were not explicitly assigned to a logical requirement in the consolidated draft above. They require clarification, consolidation, or were duplicates of content covered elsewhere. They are retained here so stakeholders can decide whether to (a) fold them into existing requirements, (b) convert them into new discrete requirements, or (c) mark them irrelevant. Several are low-clarity, repeated, or implementation-detail-only candidates. Where a candidate appears to conflict with a Must-level requirement, it is flagged for resolution rather than silently dropped.

Sources: `conversations/conv_pines014_material_volume.eml`, `conversations/conv_pines015_capacity_interface.eml`, `conversations/conv_pines016_shelf_space.eml`, `conversations/conv_pines019_020_missing_intransit.eml`, `conversations/conv_pines022_deletions.eml`, `conversations/conv_pines023_patron_characteristics.eml`, `conversations/conv_pines024_inactive_patrons.eml`, `early_draft_srs_galecia.txt`, `email_report_features.eml`, `email_staff_login.eml`, `evergreen_reference_2009.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-03-15_minutes.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`, `survey_results_2009.txt`.

Evidence candidates: C-00065, C-00066, C-00067, C-00077, C-00086, C-00089, C-00095, C-00096, C-00105, C-00106, C-00169, C-00170, C-00171, C-00172, C-00173, C-00174, C-00175, C-00176, C-00177, C-00178, C-00179, C-00180, C-00181, C-00182, C-00183, C-00184, C-00185, C-00186, C-00187, C-00188, C-00189, C-00190, C-00191, C-00192, C-00193, C-00194, C-00195, C-00196, C-00197, C-00198, C-00199, C-00200, C-00202, C-00203, C-00204, C-00209, C-00210, C-00211, C-00212, C-00213, C-00214, C-00217, C-00218, C-00219, C-00220, C-00221, C-00222, C-00223, C-00224, C-00225, C-00226, C-00227, C-00228, C-00229, C-00230, C-00231, C-00232, C-00233, C-00234, C-00235, C-00236, C-00238, C-00239, C-00240, C-00241, C-00242, C-00243, C-00244, C-00246, C-00247, C-00248, C-00249.

## Open questions and unresolved review issues

- Shelf-space estimation: which estimation algorithm should be adopted (item dimensions where available, per-format average widths, or item-count proxy)? Provide preferred default and acceptable accuracy bounds.
- Auto-revert policy specifics: what default time period should be used (suggested examples: 30 days or 90 days), and which event triggers should force immediate reversion vs. manual review?
- Retention and transaction-history window: what is the default configurable 'X days' for transaction history and for how long should detailed transaction rows be retained before aggregation to monthly/annual?
- Queue prioritization policy: what formal rules determine when a director's board report may jump ahead of staff queries? Should there be a limited number of priority escalations per time window?
- Reporting environment architecture: will the project adopt a read-only reporting replica, an ETL-fed reporting warehouse, or a mixed approach (live background jobs with caching)? Each has different cost, latency, and consistency tradeoffs.
- Export formats: beyond CSV and pivot-ready output, are there additional required export formats (e.g., Excel native, PDF for board reports)?
- Electronic activity inclusion for inactivity reports: which external digital platforms (if any) must be included and which of those produce logs that the reporting system can reliably query?
- Accessibility compliance target: confirm whether legacy browser versions (IE6, Firefox 2) remain required, or whether policy should target more recent browser versions while maintaining Section 508 compliance.
- Data-warehouse denormalization: if a denormalized reporting schema is considered for performance, who will own ETL and data sync responsibilities and what maximum acceptable replication lag is permitted?
- Clarification request for blacklisted candidates: stakeholders should review the candidate IDs listed in the blacklist and direct whether each should be (a) merged into an existing requirement above, (b) formed into a new discrete requirement, or (c) permanently discarded as out-of-scope or redundant.
- Unaccounted candidates: C-00237, C-00245, C-00250, C-00251, C-00252, C-00253, C-00254, C-00255, C-00256, C-00257, C-00258, C-00259, C-00260, C-00261, C-00262, C-00263, C-00264, C-00265, C-00266, C-00267, C-00268, C-00269, C-00270, C-00271, C-00272, C-00273, C-00274, C-00275, C-00276, C-00277, C-00278, C-00279, C-00280, C-00281, C-00282, C-00283, C-00284, C-00285, C-00286, C-00287, C-00288, C-00289, C-00290, C-00291, C-00292, C-00293, C-00294, C-00295, C-00296, C-00297, C-00298, C-00299, C-00300, C-00301, C-00302, C-00303, C-00304, C-00305, C-00306, C-00307, C-00308, C-00309, C-00310, C-00311, C-00312, C-00313, C-00314, C-00315, C-00316, C-00317, C-00318, C-00319, C-00320, C-00321, C-00322, C-00323, C-00324, C-00325, C-00326, C-00327, C-00328, C-00329, C-00330, C-00331, C-00332, C-00333, C-00334, C-00335, C-00336, C-00337, C-00338, C-00339, C-00340, C-00341, C-00342, C-00343, C-00344, C-00345, C-00346, C-00347, C-00348, C-00349, C-00350, C-00351, C-00352, C-00353, C-00354, C-00355, C-00356, C-00357, C-00358, C-00359, C-00360, C-00361, C-00362, C-00363, C-00364, C-00365, C-00366, C-00367, C-00368, C-00369, C-00370, C-00371, C-00372, C-00373, C-00374, C-00375, C-00376, C-00377, C-00378, C-00379, C-00380, C-00381, C-00382, C-00383, C-00384, C-00385, C-00386, C-00387, C-00388, C-00389, C-00390, C-00391, C-00392, C-00393, C-00394, C-00395, C-00396, C-00397, C-00398, C-00399, C-00400, C-00401, C-00402, C-00403, C-00404, C-00405, C-00406, C-00407, C-00408, C-00409, C-00410, C-00411, C-00412, C-00413, C-00414, C-00415, C-00416, C-00417, C-00418, C-00419, C-00420, C-00421, C-00422, C-00423, C-00424, C-00425, C-00426, C-00427, C-00428, C-00429, C-00430, C-00431, C-00432, C-00433, C-00434, C-00435, C-00436, C-00437, C-00438, C-00439, C-00440, C-00441, C-00442, C-00443
- Candidates assigned more than once: C-00008, C-00012, C-00014, C-00017, C-00018, C-00019, C-00020, C-00021, C-00022, C-00026, C-00051, C-00052, C-00068, C-00069, C-00071, C-00072, C-00073, C-00074, C-00079, C-00080, C-00081, C-00087, C-00088, C-00093, C-00094, C-00097, C-00098, C-00099, C-00102, C-00104, C-00106, C-00107, C-00120, C-00125, C-00131, C-00132, C-00133, C-00135, C-00136, C-00137, C-00157, C-00165, C-00168, C-00169, C-00170, C-00177, C-00179, C-00180, C-00184, C-00186, C-00187, C-00193, C-00197, C-00200, C-00201, C-00202, C-00203, C-00204, C-00205, C-00206, C-00210, C-00211, C-00212, C-00213, C-00218, C-00223, C-00224, C-00225, C-00226, C-00227, C-00228, C-00229, C-00230, C-00231, C-00232, C-00233, C-00234, C-00235, C-00236, C-00238, C-00239, C-00240, C-00241, C-00242, C-00243, C-00244, C-00246, C-00247, C-00248
- conversations/conv_pines014_material_volume.eml (CH-001): Unaccounted candidates leading to potential gaps in requirements tracking and identification.
- conversations/conv_pines014_material_volume.eml (CH-001): Duplicate candidate assignments across different requirements, potentially causing confusion.
- conversations/conv_pines015_capacity_interface.eml (CH-001): Candidates assigned more than once: C-00008, C-00012, C-00014, C-00017, C-00018, C-00019, C-00020, C-00021, C-00022, C-00026, C-00051, C-00052, C-00068, C-00069, C-00071, C-00072, C-00073, C-00074, C-00079, C-00080, C-00081, C-00087, C-00088, C-00093, C-00094, C-00097, C-00098, C-00099, C-00102, C-00104, C-00106, C-00107, C-00120, C-00125, C-00131, C-00132, C-00133, C-00135, C-00136, C-00137, C-00157, C-00165, C-00168, C-00169, C-00170, C-00177, C-00179, C-00180, C-00184, C-00186, C-00187, C-00193, C-00197, C-00200, C-00201, C-00202, C-00203, C-00204, C-00205, C-00206, C-00210, C-00211, C-00212, C-00213, C-00218, C-00223, C-00224, C-00225, C-00226, C-00227, C-00228, C-00229, C-00230, C-00231, C-00232, C-00233, C-00234, C-00235, C-00236, C-00238, C-00239, C-00240, C-00241, C-00242, C-00243, C-00244, C-00246, C-00247, C-00248
- conversations/conv_pines016_shelf_space.eml (CH-001): Unaccounted candidates: C-00237, C-00245, C-00250, C-00251, C-00252, C-00253, C-00254, C-00255, C-00256, C-00257, C-00258, C-00259, C-00260, C-00261, C-00262, C-00263, C-00264, C-00265, C-00266, C-00267, C-00268, C-00269, C-00270, C-00271, C-00272, C-00273, C-00274, C-00275, C-00276, C-00277, C-00278, C-00279, C-00280, C-00281, C-00282, C-00283, C-00284, C-00285, C-00286, C-00287, C-00288, C-00289, C-00290, C-00291, C-00292, C-00293, C-00294, C-00295, C-00296, C-00297, C-00298, C-00299, C-00300, C-00301, C-00302, C-00303, C-00304, C-00305, C-00306, C-00307, C-00308, C-00309, C-00310, C-00311, C-00312, C-00313, C-00314, C-00315, C-00316, C-00317, C-00318, C-00319, C-00320, C-00321, C-00322, C-00323, C-00324, C-00325, C-00326, C-00327, C-00328, C-00329, C-00330, C-00331, C-00332, C-00333, C-00334, C-00335, C-00336, C-00337, C-00338, C-00339, C-00340, C-00341, C-00342, C-00343, C-00344, C-00345, C-00346, C-00347, C-00348, C-00349, C-00350, C-00351, C-00352, C-00353, C-00354, C-00355, C-00356, C-00357, C-00358, C-00359, C-00360, C-00361, C-00362, C-00363, C-00364, C-00365, C-00366, C-00367, C-00368, C-00369, C-00370, C-00371, C-00372, C-00373, C-00374, C-00375, C-00376, C-00377, C-00378, C-00379, C-00380, C-00381, C-00382, C-00383, C-00384, C-00385, C-00386, C-00387, C-00388, C-00389, C-00390, C-00391, C-00392, C-00393, C-00394, C-00395, C-00396, C-00397, C-00398, C-00399, C-00400, C-00401, C-00402, C-00403, C-00404, C-00405, C-00406, C-00407, C-00408, C-00409, C-00410, C-00411, C-00412, C-00413, C-00414, C-00415, C-00416, C-00417, C-00418, C-00419, C-00420, C-00421, C-00422, C-00423, C-00424, C-00425, C-00426, C-00427, C-00428, C-00429, C-00430, C-00431, C-00432, C-00433, C-00434, C-00435, C-00436, C-00437, C-00438, C-00439, C-00440, C-00441, C-00442, C-00443
- conversations/conv_pines016_shelf_space.eml (CH-001): Candidates assigned more than once: C-00008, C-00012, C-00014, C-00017, C-00018, C-00019, C-00020, C-00021, C-00022, C-00026, C-00051, C-00052, C-00068, C-00069, C-00071, C-00072, C-00073, C-00074, C-00079, C-00080, C-00081, C-00087, C-00088, C-00093, C-00094, C-00097, C-00098, C-00099, C-00102, C-00104, C-00106, C-00107, C-00120, C-00125, C-00131, C-00132, C-00133, C-00135, C-00136, C-00137, C-00157, C-00165, C-00168, C-00169, C-00170, C-00177, C-00179, C-00180, C-00184, C-00186, C-00187, C-00193, C-00197, C-00200, C-00201, C-00202, C-00203, C-00204, C-00205, C-00206, C-00210, C-00211, C-00212, C-00213, C-00218, C-00223, C-00224, C-00225, C-00226, C-00227, C-00228, C-00229, C-00230, C-00231, C-00232, C-00233, C-00234, C-00235, C-00236, C-00238, C-00239, C-00240, C-00241, C-00242, C-00243, C-00244, C-00246, C-00247, C-00248
- conversations/conv_pines018_item_transfer.eml (CH-001): Unaccounted candidates: C-00237, C-00245, C-00250, C-00251, C-00252, C-00253, C-00254, C-00255, C-00256, C-00257, C-00258, C-00259, C-00260, C-00261, C-00262, C-00263, C-00264, C-00265, C-00266, C-00267, C-00268, C-00269, C-00270, C-00271, C-00272, C-00273, C-00274, C-00275, C-00276, C-00277, C-00278, C-00279, C-00280, C-00281, C-00282, C-00283, C-00284, C-00285, C-00286, C-00287, C-00288, C-00289, C-00290, C-00291, C-00292, C-00293, C-00294, C-00295, C-00296, C-00297, C-00298, C-00299, C-00300, C-00301, C-00302, C-00303, C-00304, C-00305, C-00306, C-00307, C-00308, C-00309, C-00310, C-00311, C-00312, C-00313, C-00314, C-00315, C-00316, C-00317, C-00318, C-00319, C-00320, C-00321, C-00322, C-00323, C-00324, C-00325, C-00326, C-00327, C-00328, C-00329, C-00330, C-00331, C-00332, C-00333, C-00334, C-00335, C-00336, C-00337, C-00338, C-00339, C-00340, C-00341, C-00342, C-00343, C-00344, C-00345, C-00346, C-00347, C-00348, C-00349, C-00350, C-00351, C-00352, C-00353, C-00354, C-00355, C-00356, C-00357, C-00358, C-00359, C-00360, C-00361, C-00362, C-00363, C-00364, C-00365, C-00366, C-00367, C-00368, C-00369, C-00370, C-00371, C-00372, C-00373, C-00374, C-00375, C-00376, C-00377, C-00378, C-00379, C-00380, C-00381, C-00382, C-00383, C-00384, C-00385, C-00386, C-00387, C-00388, C-00389, C-00390, C-00391, C-00392, C-00393, C-00394, C-00395, C-00396, C-00397, C-00398, C-00399, C-00400, C-00401, C-00402, C-00403, C-00404, C-00405, C-00406, C-00407, C-00408, C-00409, C-00410, C-00411, C-00412, C-00413, C-00414, C-00415, C-00416, C-00417, C-00418, C-00419, C-00420, C-00421, C-00422, C-00423, C-00424, C-00425, C-00426, C-00427, C-00428, C-00429, C-00430, C-00431, C-00432, C-00433, C-00434, C-00435, C-00436, C-00437, C-00438, C-00439, C-00440, C-00441, C-00442, C-00443
- conversations/conv_pines018_item_transfer.eml (CH-001): Candidates assigned more than once: C-00008, C-00012, C-00014, C-00017, C-00018, C-00019, C-00020, C-00021, C-00022, C-00026, C-00051, C-00052, C-00068, C-00069, C-00071, C-00072, C-00073, C-00074, C-00079, C-00080, C-00081, C-00087, C-00088, C-00093, C-00094, C-00097, C-00098, C-00099, C-00102, C-00104, C-00106, C-00107, C-00120, C-00125, C-00131, C-00132, C-00133, C-00135, C-00136, C-00137, C-00157, C-00165, C-00168, C-00169, C-00170, C-00177, C-00179, C-00180, C-00184, C-00186, C-00187, C-00193, C-00197, C-00200, C-00201, C-00202, C-00203, C-00204, C-00205, C-00206, C-00210, C-00211, C-00212, C-00213, C-00218, C-00223, C-00224, C-00225, C-00226, C-00227, C-00228, C-00229, C-00230, C-00231, C-00232, C-00233, C-00234, C-00235, C-00236, C-00238, C-00239, C-00240, C-00241, C-00242, C-00243, C-00244, C-00246, C-00247, C-00248
- conversations/conv_pines019_020_missing_intransit.eml (CH-001): Numerical thresholds for item purging and retention need clarification. Specific thresholds for auto-revert mechanisms are not identified. Stakeholders need to validate filtering logic for patrons with outstanding fines during inactivity checks.
- conversations/conv_pines019_020_missing_intransit.eml (CH-001): Multiple requirements on shelf-space estimation and auto-reversion are scattered across sections.
- conversations/conv_pines021_item_purging.eml (CH-001): Unassigned candidates present in the corpus didn't get matched to requirements, leading to gaps in fulfillment options.
- conversations/conv_pines021_item_purging.eml (CH-001): Some candidates are duplicated across different requirements, creating confusion in tracking their implementation.
- conversations/conv_pines022_deletions.eml (CH-001): Unaccounted candidates: C-00237, C-00245, C-00250, C-00251, C-00252, C-00253, C-00254, C-00255, C-00256, C-00257, C-00258, C-00259, C-00260, C-00261, C-00262, C-00263, C-00264, C-00265, C-00266, C-00267, C-00268, C-00269, C-00270, C-00271, C-00272, C-00273, C-00274, C-00275, C-00276, C-00277, C-00278, C-00279, C-00280, C-00281, C-00282, C-00283, C-00284, C-00285, C-00286, C-00287, C-00288, C-00289, C-00290, C-00291, C-00292, C-00293, C-00294, C-00295, C-00296, C-00297, C-00298, C-00299, C-00300, C-00301, C-00302, C-00303, C-00304, C-00305, C-00306, C-00307, C-00308, C-00309, C-00310, C-00311, C-00312, C-00313, C-00314, C-00315, C-00316, C-00317, C-00318, C-00319, C-00320, C-00321, C-00322, C-00323, C-00324, C-00325, C-00326, C-00327, C-00328, C-00329, C-00330, C-00331, C-00332, C-00333, C-00334, C-00335, C-00336, C-00337, C-00338, C-00339, C-00340, C-00341, C-00342, C-00343, C-00344, C-00345, C-00346, C-00347, C-00348, C-00349, C-00350, C-00351, C-00352, C-00353, C-00354, C-00355, C-00356, C-00357, C-00358, C-00359, C-00360, C-00361, C-00362, C-00363, C-00364, C-00365, C-00366, C-00367, C-00368, C-00369, C-00370, C-00371, C-00372, C-00373, C-00374, C-00375, C-00376, C-00377, C-00378, C-00379, C-00380, C-00381, C-00382, C-00383, C-00384, C-00385, C-00386, C-00387, C-00388, C-00389, C-00390, C-00391, C-00392, C-00393, C-00394, C-00395, C-00396, C-00397, C-00398, C-00399, C-00400, C-00401, C-00402, C-00403, C-00404, C-00405, C-00406, C-00407, C-00408, C-00409, C-00410, C-00411, C-00412, C-00413, C-00414, C-00415, C-00416, C-00417, C-00418, C-00419, C-00420, C-00421, C-00422, C-00423, C-00424, C-00425, C-00426, C-00427, C-00428, C-00429, C-00430, C-00431, C-00432, C-00433, C-00434, C-00435, C-00436, C-00437, C-00438, C-00439, C-00440, C-00441, C-00442, C-00443
- conversations/conv_pines022_deletions.eml (CH-001): Candidates assigned more than once: C-00008, C-00012, C-00014, C-00017, C-00018, C-00019, C-00020, C-00021, C-00022, C-00026, C-00051, C-00052, C-00068, C-00069, C-00071, C-00072, C-00073, C-00074, C-00079, C-00080, C-00081, C-00087, C-00088, C-00093, C-00094, C-00097, C-00098, C-00099, C-00102, C-00104, C-00106, C-00107, C-00120, C-00125, C-00131, C-00132, C-00133, C-00135, C-00136, C-00137, C-00157, C-00165, C-00168, C-00169, C-00170, C-00177, C-00179, C-00180, C-00184, C-00186, C-00187, C-00193, C-00197, C-00200, C-00201, C-00202, C-00203, C-00204, C-00205, C-00206, C-00210, C-00211, C-00212, C-00213, C-00218, C-00223, C-00224, C-00225, C-00226, C-00227, C-00228, C-00229, C-00230, C-00231, C-00232, C-00233, C-00234, C-00235, C-00236, C-00238, C-00239, C-00240, C-00241, C-00242, C-00243, C-00244, C-00246, C-00247, C-00248
- conversations/conv_pines023_patron_characteristics.eml (CH-001): Unaccounted candidates: C-00237, C-00245, C-00250, C-00251, C-00252, C-00253, C-00254, C-00255, C-00256, C-00257, C-00258, C-00259, C-00260, C-00261, C-00262, C-00263, C-00264, C-00265, C-00266, C-00267, C-00268, C-00269, C-00270, C-00271, C-00272, C-00273, C-00274, C-00275, C-00276, C-00277, C-00278, C-00279, C-00280, C-00281, C-00282, C-00283, C-00284, C-00285, C-00286, C-00287, C-00288, C-00289, C-00290, C-00291, C-00292, C-00293, C-00294, C-00295, C-00296, C-00297, C-00298, C-00299, C-00300, C-00301, C-00302, C-00303, C-00304, C-00305, C-00306, C-00307, C-00308, C-00309, C-00310, C-00311, C-00312, C-00313, C-00314, C-00315, C-00316, C-00317, C-00318, C-00319, C-00320, C-00321, C-00322, C-00323, C-00324, C-00325, C-00326, C-00327, C-00328, C-00329, C-00330, C-00331, C-00332, C-00333, C-00334, C-00335, C-00336, C-00337, C-00338, C-00339, C-00340, C-00341, C-00342, C-00343, C-00344, C-00345, C-00346, C-00347, C-00348, C-00349, C-00350, C-00351, C-00352, C-00353, C-00354, C-00355, C-00356, C-00357, C-00358, C-00359, C-00360, C-00361, C-00362, C-00363, C-00364, C-00365, C-00366, C-00367, C-00368, C-00369, C-00370, C-00371, C-00372, C-00373, C-00374, C-00375, C-00376, C-00377, C-00378, C-00379, C-00380, C-00381, C-00382, C-00383, C-00384, C-00385, C-00386, C-00387, C-00388, C-00389, C-00390, C-00391, C-00392, C-00393, C-00394, C-00395, C-00396, C-00397, C-00398, C-00399, C-00400, C-00401, C-00402, C-00403, C-00404, C-00405, C-00406, C-00407, C-00408, C-00409, C-00410, C-00411, C-00412, C-00413, C-00414, C-00415, C-00416, C-00417, C-00418, C-00419, C-00420, C-00421, C-00422, C-00423, C-00424, C-00425, C-00426, C-00427, C-00428, C-00429, C-00430, C-00431, C-00432, C-00433, C-00434, C-00435, C-00436, C-00437, C-00438, C-00439, C-00440, C-00441, C-00442, C-00443
- conversations/conv_pines023_patron_characteristics.eml (CH-001): Candidates assigned more than once: C-00008, C-00012, C-00014, C-00017, C-00018, C-00019, C-00020, C-00021, C-00022, C-00026, C-00051, C-00052, C-00068, C-00069, C-00071, C-00072, C-00073, C-00074, C-00079, C-00080, C-00081, C-00087, C-00088, C-00093, C-00094, C-00097, C-00098, C-00099, C-00102, C-00104, C-00106, C-00107, C-00120, C-00125, C-00131, C-00132, C-00133, C-00135, C-00136, C-00137, C-00157, C-00165, C-00168, C-00169, C-00170, C-00177, C-00179, C-00180, C-00184, C-00186, C-00187, C-00193, C-00197, C-00200, C-00201, C-00202, C-00203, C-00204, C-00205, C-00206, C-00210, C-00211, C-00212, C-00213, C-00218, C-00223, C-00224, C-00225, C-00226, C-00227, C-00228, C-00229, C-00230, C-00231, C-00232, C-00233, C-00234, C-00235, C-00236, C-00238, C-00239, C-00240, C-00241, C-00242, C-00243, C-00244, C-00246, C-00247, C-00248
- conversations/conv_pines024_inactive_patrons.eml (CH-001): Unaccounted candidates: C-00237, C-00245, C-00250, C-00251, C-00252, C-00253, C-00254, C-00255, C-00256, C-00257, C-00258, C-00259, C-00260, C-00261, C-00262, C-00263, C-00264, C-00265, C-00266, C-00267, C-00268, C-00269, C-00270, C-00271, C-00272, C-00273, C-00274, C-00275, C-00276, C-00277, C-00278, C-00279, C-00280, C-00281, C-00282, C-00283, C-00284, C-00285, C-00286, C-00287, C-00288, C-00289, C-00290, C-00291, C-00292, C-00293, C-00294, C-00295, C-00296, C-00297, C-00298, C-00299, C-00300, C-00301, C-00302, C-00303, C-00304, C-00305, C-00306, C-00307, C-00308, C-00309, C-00310, C-00311, C-00312, C-00313, C-00314, C-00315, C-00316, C-00317, C-00318, C-00319, C-00320, C-00321, C-00322, C-00323, C-00324, C-00325, C-00326, C-00327, C-00328, C-00329, C-00330, C-00331, C-00332, C-00333, C-00334, C-00335, C-00336, C-00337, C-00338, C-00339, C-00340, C-00341, C-00342, C-00343, C-00344, C-00345, C-00346, C-00347, C-00348, C-00349, C-00350, C-00351, C-00352, C-00353, C-00354, C-00355, C-00356, C-00357, C-00358, C-00359, C-00360, C-00361, C-00362, C-00363, C-00364, C-00365, C-00366, C-00367, C-00368, C-00369, C-00370, C-00371, C-00372, C-00373, C-00374, C-00375, C-00376, C-00377, C-00378, C-00379, C-00380, C-00381, C-00382, C-00383, C-00384, C-00385, C-00386, C-00387, C-00388, C-00389, C-00390, C-00391, C-00392, C-00393, C-00394, C-00395, C-00396, C-00397, C-00398, C-00399, C-00400, C-00401, C-00402, C-00403, C-00404, C-00405, C-00406, C-00407, C-00408, C-00409, C-00410, C-00411, C-00412, C-00413, C-00414, C-00415, C-00416, C-00417, C-00418, C-00419, C-00420, C-00421, C-00422, C-00423, C-00424, C-00425, C-00426, C-00427, C-00428, C-00429, C-00430, C-00431, C-00432, C-00433, C-00434, C-00435, C-00436, C-00437, C-00438, C-00439, C-00440, C-00441, C-00442, C-00443
- conversations/conv_pines024_inactive_patrons.eml (CH-001): Candidates assigned more than once: C-00008, C-00012, C-00014, C-00017, C-00018, C-00019, C-00020, C-00021, C-00022, C-00026, C-00051, C-00052, C-00068, C-00069, C-00071, C-00072, C-00073, C-00074, C-00079, C-00080, C-00081, C-00087, C-00088, C-00093, C-00094, C-00097, C-00098, C-00099, C-00102, C-00104, C-00106, C-00107, C-00120, C-00125, C-00131, C-00132, C-00133, C-00135, C-00136, C-00137, C-00157, C-00165, C-00168, C-00169, C-00170, C-00177, C-00179, C-00180, C-00184, C-00186, C-00187, C-00193, C-00197, C-00200, C-00201, C-00202, C-00203, C-00204, C-00205, C-00206, C-00210, C-00211, C-00212, C-00213, C-00218, C-00223, C-00224, C-00225, C-00226, C-00227, C-00228, C-00229, C-00230, C-00231, C-00232, C-00233, C-00234, C-00235, C-00236, C-00238, C-00239, C-00240, C-00241, C-00242, C-00243, C-00244, C-00246, C-00247, C-00248
- early_draft_srs_galecia.txt (CH-001): Unaccounted candidates exist that are not linked to specific requirements, leading to ambiguity in the underlying specifications and requirement fulfillment.
- early_draft_srs_galecia.txt (CH-001): There are candidates assigned more than once, which could cause confusion in the tracking of requirements.
- early_draft_srs_galecia.txt (CH-002): Unaccounted candidates: C-00237, C-00245, C-00250, C-00251, C-00252, C-00253, C-00254, C-00255, C-00256, C-00257, C-00258, C-00259, C-00260, C-00261, C-00262, C-00263, C-00264, C-00265, C-00266, C-00267, C-00268, C-00269, C-00270, C-00271, C-00272, C-00273, C-00274, C-00275, C-00276, C-00277, C-00278, C-00279, C-00280, C-00281, C-00282, C-00283, C-00284, C-00285, C-00286, C-00287, C-00288, C-00289, C-00290, C-00291, C-00292, C-00293, C-00294, C-00295, C-00296, C-00297, C-00298, C-00299, C-00300, C-00301, C-00302, C-00303, C-00304, C-00305, C-00306, C-00307, C-00308, C-00309, C-00310, C-00311, C-00312, C-00313, C-00314, C-00315, C-00316, C-00317, C-00318, C-00319, C-00320, C-00321, C-00322, C-00323, C-00324, C-00325, C-00326, C-00327, C-00328, C-00329, C-00330, C-00331, C-00332, C-00333, C-00334, C-00335, C-00336, C-00337, C-00338, C-00339, C-00340, C-00341, C-00342, C-00343, C-00344, C-00345, C-00346, C-00347, C-00348, C-00349, C-00350, C-00351, C-00352, C-00353, C-00354, C-00355, C-00356, C-00357, C-00358, C-00359, C-00360, C-00361, C-00362, C-00363, C-00364, C-00365, C-00366, C-00367, C-00368, C-00369, C-00370, C-00371, C-00372, C-00373, C-00374, C-00375, C-00376, C-00377, C-00378, C-00379, C-00380, C-00381, C-00382, C-00383, C-00384, C-00385, C-00386, C-00387, C-00388, C-00389, C-00390, C-00391, C-00392, C-00393, C-00394, C-00395, C-00396, C-00397, C-00398, C-00399, C-00400, C-00401, C-00402, C-00403, C-00404, C-00405, C-00406, C-00407, C-00408, C-00409, C-00410, C-00411, C-00412, C-00413, C-00414, C-00415, C-00416, C-00417, C-00418, C-00419, C-00420, C-00421, C-00422, C-00423, C-00424, C-00425, C-00426, C-00427, C-00428, C-00429, C-00430, C-00431, C-00432, C-00433, C-00434, C-00435, C-00436, C-00437, C-00438, C-00439, C-00440, C-00441, C-00442, C-00443
- early_draft_srs_galecia.txt (CH-002): Candidates assigned more than once: C-00008, C-00012, C-00014, C-00017, C-00018, C-00019, C-00020, C-00021, C-00022, C-00026, C-00051, C-00052, C-00068, C-00069, C-00071, C-00072, C-00073, C-00074, C-00079, C-00080, C-00081, C-00087, C-00088, C-00093, C-00094, C-00097, C-00098, C-00099, C-00102, C-00104, C-00106, C-00107, C-00120, C-00125, C-00131, C-00132, C-00133, C-00135, C-00136, C-00137, C-00157, C-00165, C-00168, C-00169, C-00170, C-00177, C-00179, C-00180, C-00184, C-00186, C-00187, C-00193, C-00197, C-00200, C-00201, C-00202, C-00203, C-00204, C-00205, C-00206, C-00210, C-00211, C-00212, C-00213, C-00218, C-00223, C-00224, C-00225, C-00226, C-00227, C-00228, C-00229, C-00230, C-00231, C-00232, C-00233, C-00234, C-00235, C-00236, C-00238, C-00239, C-00240, C-00241, C-00242, C-00243, C-00244, C-00246, C-00247, C-00248
- early_draft_srs_galecia.txt (CH-003): Unaccounted candidates: C-00237, C-00245, C-00250, C-00251, C-00252, C-00253, C-00254, C-00255, C-00256, C-00257, C-00258, C-00259, C-00260, C-00261, C-00262, C-00263, C-00264, C-00265, C-00266, C-00267, C-00268, C-00269, C-00270, C-00271, C-00272, C-00273, C-00274, C-00275, C-00276, C-00277, C-00278, C-00279, C-00280, C-00281, C-00282, C-00283, C-00284, C-00285, C-00286, C-00287, C-00288, C-00289, C-00290, C-00291, C-00292, C-00293, C-00294, C-00295, C-00296, C-00297, C-00298, C-00299, C-00300, C-00301, C-00302, C-00303, C-00304, C-00305, C-00306, C-00307, C-00308, C-00309, C-00310, C-00311, C-00312, C-00313, C-00314, C-00315, C-00316, C-00317, C-00318, C-00319, C-00320, C-00321, C-00322, C-00323, C-00324, C-00325, C-00326, C-00327, C-00328, C-00329, C-00330, C-00331, C-00332, C-00333, C-00334, C-00335, C-00336, C-00337, C-00338, C-00339, C-00340, C-00341, C-00342, C-00343, C-00344, C-00345, C-00346, C-00347, C-00348, C-00349, C-00350, C-00351, C-00352, C-00353, C-00354, C-00355, C-00356, C-00357, C-00358, C-00359, C-00360, C-00361, C-00362, C-00363, C-00364, C-00365, C-00366, C-00367, C-00368, C-00369, C-00370, C-00371, C-00372, C-00373, C-00374, C-00375, C-00376, C-00377, C-00378, C-00379, C-00380, C-00381, C-00382, C-00383, C-00384, C-00385, C-00386, C-00387, C-00388, C-00389, C-00390, C-00391, C-00392, C-00393, C-00394, C-00395, C-00396, C-00397, C-00398, C-00399, C-00400, C-00401, C-00402, C-00403, C-00404, C-00405, C-00406, C-00407, C-00408, C-00409, C-00410, C-00411, C-00412, C-00413, C-00414, C-00415, C-00416, C-00417, C-00418, C-00419, C-00420, C-00421, C-00422, C-00423, C-00424, C-00425, C-00426, C-00427, C-00428, C-00429, C-00430, C-00431, C-00432, C-00433, C-00434, C-00435, C-00436, C-00437, C-00438, C-00439, C-00440, C-00441, C-00442, C-00443
- early_draft_srs_galecia.txt (CH-003): Candidates assigned more than once: C-00008, C-00012, C-00014, C-00017, C-00018, C-00019, C-00020, C-00021, C-00022, C-00026, C-00051, C-00052, C-00068, C-00069, C-00071, C-00072, C-00073, C-00074, C-00079, C-00080, C-00081, C-00087, C-00088, C-00093, C-00094, C-00097, C-00098, C-00099, C-00102, C-00104, C-00106, C-00107, C-00120, C-00125, C-00131, C-00132, C-00133, C-00135, C-00136, C-00137, C-00157, C-00165, C-00168, C-00169, C-00170, C-00177, C-00179, C-00180, C-00184, C-00186, C-00187, C-00193, C-00197, C-00200, C-00201, C-00202, C-00203, C-00204, C-00205, C-00206, C-00210, C-00211, C-00212, C-00213, C-00218, C-00223, C-00224, C-00225, C-00226, C-00227, C-00228, C-00229, C-00230, C-00231, C-00232, C-00233, C-00234, C-00235, C-00236, C-00238, C-00239, C-00240, C-00241, C-00242, C-00243, C-00244, C-00246, C-00247, C-00248
- email_financial_reports.eml (CH-001): Candidates assigned more than once: C-00008, C-00012, C-00014, C-00017, C-00018, C-00019, C-00020, C-00021, C-00022, C-00026, C-00051, C-00052, C-00068, C-00069, C-00071, C-00072, C-00073, C-00074, C-00079, C-00080, C-00081, C-00087, C-00088, C-00093, C-00094, C-00097, C-00098, C-00099, C-00102, C-00104, C-00106, C-00107, C-00120, C-00125, C-00131, C-00132, C-00133, C-00135, C-00136, C-00137, C-00157, C-00165, C-00168, C-00169, C-00170, C-00177, C-00179, C-00180, C-00184, C-00186, C-00187, C-00193, C-00197, C-00200, C-00201, C-00202, C-00203, C-00204, C-00205, C-00206, C-00210, C-00211, C-00212, C-00213, C-00218, C-00223, C-00224, C-00225, C-00226, C-00227, C-00228, C-00229, C-00230, C-00231, C-00232, C-00233, C-00234, C-00235, C-00236, C-00238, C-00239, C-00240, C-00241, C-00242, C-00243, C-00244, C-00246, C-00247, C-00248
- email_report_features.eml (CH-001): Unaccounted candidates: C-00237, C-00245, C-00250, C-00251, C-00252, C-00253, C-00254, C-00255, C-00256, C-00257, C-00258, C-00259, C-00260, C-00261, C-00262, C-00263, C-00264, C-00265, C-00266, C-00267, C-00268, C-00269, C-00270, C-00271, C-00272, C-00273, C-00274, C-00275, C-00276, C-00277, C-00278, C-00279, C-00280, C-00281, C-00282, C-00283, C-00284, C-00285, C-00286, C-00287, C-00288, C-00289, C-00290, C-00291, C-00292, C-00293, C-00294, C-00295, C-00296, C-00297, C-00298, C-00299, C-00300, C-00301, C-00302, C-00303, C-00304, C-00305, C-00306, C-00307, C-00308, C-00309, C-00310, C-00311, C-00312, C-00313, C-00314, C-00315, C-00316, C-00317, C-00318, C-00319, C-00320, C-00321, C-00322, C-00323, C-00324, C-00325, C-00326, C-00327, C-00328, C-00329, C-00330, C-00331, C-00332, C-00333, C-00334, C-00335, C-00336, C-00337, C-00338, C-00339, C-00340, C-00341, C-00342, C-00343, C-00344, C-00345, C-00346, C-00347, C-00348, C-00349, C-00350, C-00351, C-00352, C-00353, C-00354, C-00355, C-00356, C-00357, C-00358, C-00359, C-00360, C-00361, C-00362, C-00363, C-00364, C-00365, C-00366, C-00367, C-00368, C-00369, C-00370, C-00371, C-00372, C-00373, C-00374, C-00375, C-00376, C-00377, C-00378, C-00379, C-00380, C-00381, C-00382, C-00383, C-00384, C-00385, C-00386, C-00387, C-00388, C-00389, C-00390, C-00391, C-00392, C-00393, C-00394, C-00395, C-00396, C-00397, C-00398, C-00399, C-00400, C-00401, C-00402, C-00403, C-00404, C-00405, C-00406, C-00407, C-00408, C-00409, C-00410, C-00411, C-00412, C-00413, C-00414, C-00415, C-00416, C-00417, C-00418, C-00419, C-00420, C-00421, C-00422, C-00423, C-00424, C-00425, C-00426, C-00427, C-00428, C-00429, C-00430, C-00431, C-00432, C-00433, C-00434, C-00435, C-00436, C-00437, C-00438, C-00439, C-00440, C-00441, C-00442, C-00443
- email_report_features.eml (CH-001): Candidates assigned more than once: C-00008, C-00012, C-00014, C-00017, C-00018, C-00019, C-00020, C-00021, C-00022, C-00026, C-00051, C-00052, C-00068, C-00069, C-00071, C-00072, C-00073, C-00074, C-00079, C-00080, C-00081, C-00087, C-00088, C-00093, C-00094, C-00097, C-00098, C-00099, C-00102, C-00104, C-00106, C-00107, C-00120, C-00125, C-00131, C-00132, C-00133, C-00135, C-00136, C-00137, C-00157, C-00165, C-00168, C-00169, C-00170, C-00177, C-00179, C-00180, C-00184, C-00186, C-00187, C-00193, C-00197, C-00200, C-00201, C-00202, C-00203, C-00204, C-00205, C-00206, C-00210, C-00211, C-00212, C-00213, C-00218, C-00223, C-00224, C-00225, C-00226, C-00227, C-00228, C-00229, C-00230, C-00231, C-00232, C-00233, C-00234, C-00235, C-00236, C-00238, C-00239, C-00240, C-00241, C-00242, C-00243, C-00244, C-00246, C-00247, C-00248
- email_staff_login.eml (CH-001): Candidates assigned more than once: C-00008, C-00012, C-00014, C-00017, C-00018, C-00019, C-00020, C-00021, C-00022, C-00026, C-00051, C-00052, C-00068, C-00069, C-00071, C-00072, C-00073, C-00074, C-00079, C-00080, C-00081, C-00087, C-00088, C-00093, C-00094, C-00097, C-00098, C-00099, C-00102, C-00104, C-00106, C-00107, C-00120, C-00125, C-00131, C-00132, C-00133, C-00135, C-00136, C-00137, C-00157, C-00165, C-00168, C-00169, C-00170, C-00177, C-00179, C-00180, C-00184, C-00186, C-00187, C-00193, C-00197, C-00200, C-00201, C-00202, C-00203, C-00204, C-00205, C-00206, C-00210, C-00211, C-00212, C-00213, C-00218, C-00223, C-00224, C-00225, C-00226, C-00227, C-00228, C-00229, C-00230, C-00231, C-00232, C-00233, C-00234, C-00235, C-00236, C-00238, C-00239, C-00240, C-00241, C-00242, C-00243, C-00244, C-00246, C-00247, C-00248
- evergreen_reference_2009.txt (CH-001): Unaccounted candidates: C-00237, C-00245, C-00250, C-00251, C-00252, C-00253, C-00254, C-00255, C-00256, C-00257, C-00258, C-00259, C-00260, C-00261, C-00262, C-00263, C-00264, C-00265, C-00266, C-00267, C-00268, C-00269, C-00270, C-00271, C-00272, C-00273, C-00274, C-00275, C-00276, C-00277, C-00278, C-00279, C-00280, C-00281, C-00282, C-00283, C-00284, C-00285, C-00286, C-00287, C-00288, C-00289, C-00290, C-00291, C-00292, C-00293, C-00294, C-00295, C-00296, C-00297, C-00298, C-00299, C-00300, C-00301, C-00302, C-00303, C-00304, C-00305, C-00306, C-00307, C-00308, C-00309, C-00310, C-00311, C-00312, C-00313, C-00314, C-00315, C-00316, C-00317, C-00318, C-00319, C-00320, C-00321, C-00322, C-00323, C-00324, C-00325, C-00326, C-00327, C-00328, C-00329, C-00330, C-00331, C-00332, C-00333, C-00334, C-00335, C-00336, C-00337, C-00338, C-00339, C-00340, C-00341, C-00342, C-00343, C-00344, C-00345, C-00346, C-00347, C-00348, C-00349, C-00350, C-00351, C-00352, C-00353, C-00354, C-00355, C-00356, C-00357, C-00358, C-00359, C-00360, C-00361, C-00362, C-00363, C-00364, C-00365, C-00366, C-00367, C-00368, C-00369, C-00370, C-00371, C-00372, C-00373, C-00374, C-00375, C-00376, C-00377, C-00378, C-00379, C-00380, C-00381, C-00382, C-00383, C-00384, C-00385, C-00386, C-00387, C-00388, C-00389, C-00390, C-00391, C-00392, C-00393, C-00394, C-00395, C-00396, C-00397, C-00398, C-00399, C-00400, C-00401, C-00402, C-00403, C-00404, C-00405, C-00406, C-00407, C-00408, C-00409, C-00410, C-00411, C-00412, C-00413, C-00414, C-00415, C-00416, C-00417, C-00418, C-00419, C-00420
- interview_cataloging_2009-05-08.txt (CH-001): Unaccounted candidates: C-00237, C-00245, C-00250, C-00251, C-00252, C-00253, C-00254, C-00255, C-00256, C-00257, C-00258, C-00259, C-00260, C-00261, C-00262, C-00263, C-00264, C-00265, C-00266, C-00267, C-00268, C-00269, C-00270, C-00271, C-00272, C-00273, C-00274, C-00275, C-00276, C-00277, C-00278, C-00279, C-00280, C-00281, C-00282, C-00283, C-00284, C-00285, C-00286, C-00287, C-00288, C-00289, C-00290, C-00291, C-00292, C-00293, C-00294, C-00295, C-00296, C-00297, C-00298, C-00299, C-00300, C-00301, C-00302, C-00303, C-00304, C-00305, C-00306, C-00307, C-00308, C-00309, C-00310, C-00311, C-00312, C-00313, C-00314, C-00315, C-00316, C-00317, C-00318, C-00319, C-00320, C-00321, C-00322, C-00323, C-00324, C-00325, C-00326, C-00327, C-00328, C-00329, C-00330, C-00331, C-00332, C-00333, C-00334, C-00335, C-00336, C-00337, C-00338, C-00339, C-00340, C-00341, C-00342, C-00343, C-00344, C-00345, C-00346, C-00347, C-00348, C-00349, C-00350, C-00351, C-00352, C-00353, C-00354, C-00355, C-00356, C-00357, C-00358, C-00359, C-00360, C-00361, C-00362, C-00363, C-00364, C-00365, C-00366, C-00367, C-00368, C-00369, C-00370, C-00371, C-00372, C-00373, C-00374, C-00375, C-00376, C-00377, C-00378, C-00379, C-00380, C-00381, C-00382, C-00383, C-00384, C-00385, C-00386, C-00387, C-00388, C-00389, C-00390, C-00391, C-00392, C-00393, C-00394, C-00395, C-00396, C-00397, C-00398, C-00399, C-00400, C-00401, C-00402, C-00403, C-00404, C-00405, C-00406, C-00407, C-00408, C-00409, C-00410, C-00411, C-00412, C-00413, C-00414, C-00415, C-00416, C-00417, C-00418, C-00419, C-00420
- interview_cataloging_2009-05-08.txt (CH-001): Candidates assigned more than once: C-00008, C-00012, C-00014, C-00017, C-00018, C-00019, C-00020, C-00021, C-00022, C-00026, C-00051, C-00052, C-00068, C-00069, C-00071, C-00072, C-00073, C-00074, C-00079, C-00080, C-00081, C-00087, C-00088, C-00093, C-00094, C-00097, C-00098, C-00099, C-00102, C-00104, C-00106, C-00107, C-00120, C-00125, C-00131, C-00132, C-00133, C-00135, C-00136, C-00137, C-00157, C-00165, C-00168, C-00169, C-00170, C-00177, C-00179, C-00180, C-00184, C-00186, C-00187, C-00193, C-00197, C-00200, C-00201, C-00202, C-00203, C-00204, C-00205, C-00206, C-00210, C-00211, C-00212, C-00213, C-00218, C-00223, C-00224, C-00225, C-00226, C-00227, C-00228, C-00229, C-00230, C-00231, C-00232, C-00233, C-00234, C-00235, C-00236, C-00238, C-00239, C-00240, C-00241, C-00242, C-00243, C-00244, C-00246, C-00247, C-00248
- interview_sysadmin_2009-05-10.txt (CH-001): Unaccounted candidates: C-00237, C-00245, C-00250, C-00251, C-00252, C-00253, C-00254, C-00255, C-00256, C-00257, C-00258, C-00259, C-00260, C-00261, C-00262, C-00263, C-00264, C-00265, C-00266, C-00267, C-00268, C-00269, C-00270, C-00271, C-00272, C-00273, C-00274, C-00275, C-00276, C-00277, C-00278, C-00279, C-00280, C-00281, C-00282, C-00283, C-00284, C-00285, C-00286, C-00287, C-00288, C-00289, C-00290, C-00291, C-00292, C-00293, C-00294, C-00295, C-00296, C-00297, C-00298, C-00299, C-00300, C-00301, C-00302, C-00303, C-00304, C-00305, C-00306, C-00307, C-00308, C-00309, C-00310, C-00311, C-00312, C-00313, C-00314, C-00315, C-00316, C-00317, C-00318, C-00319, C-00320, C-00321, C-00322, C-00323, C-00324, C-00325, C-00326, C-00327, C-00328, C-00329, C-00330, C-00331, C-00332, C-00333, C-00334, C-00335, C-00336, C-00337, C-00338, C-00339, C-00340, C-00341, C-00342, C-00343, C-00344, C-00345, C-00346, C-00347, C-00348, C-00349, C-00350, C-00351, C-00352, C-00353, C-00354, C-00355, C-00356, C-00357, C-00358, C-00359, C-00360, C-00361, C-00362, C-00363, C-00364, C-00365, C-00366, C-00367, C-00368, C-00369, C-00370, C-00371, C-00372, C-00373, C-00374, C-00375, C-00376, C-00377, C-00378, C-00379, C-00380, C-00381, C-00382, C-00383, C-00384, C-00385, C-00386, C-00387, C-00388, C-00389, C-00390, C-00391, C-00392, C-00393, C-00394, C-00395, C-00396, C-00397, C-00398, C-00399, C-00400, C-00401, C-00402, C-00403, C-00404, C-00405, C-00406, C-00407, C-00408, C-00409, C-00410, C-00411
- meeting_minutes/meeting_2009-03-15_minutes.txt (CH-001): Deterministic issues with unaccounted candidates.
- meeting_minutes/meeting_2009-03-15_minutes.txt (CH-001): Duplicate candidate assignments identified.
- meeting_minutes/meeting_2009-07-20_minutes.txt (CH-001): Several candidates have been identified with overlapping requirements and are either unassigned or described more than once, necessitating clarity and consolidation.
- meeting_tech_subcommittee_2009-06-30.txt (CH-001): Unaccounted candidates: C-00237, C-00245, C-00250, C-00251, C-00252, C-00253, C-00254, C-00255, C-00256, C-00257, C-00258, C-00259, C-00260, C-00261, C-00262, C-00263, C-00264, C-00265, C-00266, C-00267, C-00268, C-00269, C-00270, C-00271, C-00272, C-00273, C-00274, C-00275, C-00276, C-00277, C-00278, C-00279, C-00280, C-00281, C-00282, C-00283, C-00284, C-00285, C-00286, C-00287, C-00288, C-00289, C-00290, C-00291, C-00292, C-00293, C-00294, C-00295, C-00296, C-00297, C-00298, C-00299, C-00300, C-00301, C-00302, C-00303, C-00304, C-00305, C-00306, C-00307, C-00308, C-00309, C-00310, C-00311, C-00312, C-00313, C-00314, C-00315, C-00316, C-00317, C-00318, C-00319, C-00320, C-00321, C-00322, C-00323, C-00324, C-00325, C-00326, C-00327, C-00328, C-00329, C-00330, C-00331, C-00332, C-00333, C-00334, C-00335, C-00336, C-00337, C-00338, C-00339, C-00340, C-00341, C-00342, C-00343, C-00344, C-00345, C-00346, C-00347, C-00348, C-00349, C-00350, C-00351, C-00352, C-00353, C-00354, C-00355, C-00356, C-00357, C-00358, C-00359, C-00360, C-00361, C-00362, C-00363, C-00364, C-00365, C-00366, C-00367, C-00368, C-00369, C-00370, C-00371, C-00372, C-00373, C-00374, C-00375, C-00376, C-00377, C-00378, C-00379, C-00380, C-00381, C-00382, C-00383, C-00384, C-00385, C-00386, C-00387, C-00388, C-00389, C-00390, C-00391, C-00392, C-00393, C-00394, C-00395, C-00396, C-00397, C-00398, C-00399, C-00400, C-00401, C-00402, C-00403, C-00404, C-00405, C-00406, C-00407, C-00408, C-00409, C-00410, C-00411, C-00412, C-00413, C-00414, C-00415, C-00416, C-00417, C-00418, C-00419, C-00420, C-00421, C-00422, C-00423, C-00424, C-00425, C-00426, C-00427, C-00428, C-00429, C-00430, C-00431, C-00432, C-00433, C-00434, C-00435, C-00436, C-00437, C-00438, C-00439, C-00440, C-00441, C-00442, C-00443
- survey_results_2009.txt (CH-001): Unaccounted candidates: C-00237, C-00245, C-00250, C-00251, C-00252, C-00253, C-00254, C-00255, C-00256, C-00257, C-00258, C-00259, C-00260, C-00261, C-00262, C-00263, C-00264, C-00265, C-00266, C-00267, C-00268, C-00269, C-00270, C-00271, C-00272, C-00273, C-00274, C-00275, C-00276, C-00277, C-00278, C-00279, C-00280, C-00281, C-00282, C-00283, C-00284, C-00285, C-00286, C-00287, C-00288, C-00289, C-00290, C-00291, C-00292, C-00293, C-00294, C-00295, C-00296, C-00297, C-00298, C-00299, C-00300, C-00301, C-00302, C-00303, C-00304, C-00305, C-00306, C-00307, C-00308, C-00309, C-00310, C-00311, C-00312, C-00313, C-00314, C-00315, C-00316, C-00317, C-00318, C-00319, C-00320, C-00321, C-00322, C-00323, C-00324, C-00325, C-00326, C-00327, C-00328, C-00329, C-00330, C-00331, C-00332, C-00333, C-00334, C-00335, C-00336, C-00337, C-00338, C-00339, C-00340, C-00341, C-00342, C-00343, C-00344, C-00345, C-00346, C-00347, C-00348, C-00349, C-00350, C-00351, C-00352, C-00353, C-00354, C-00355, C-00356, C-00357, C-00358, C-00359, C-00360, C-00361, C-00362, C-00363, C-00364, C-00365, C-00366, C-00367, C-00368, C-00369, C-00370, C-00371, C-00372, C-00373, C-00374, C-00375, C-00376, C-00377, C-00378, C-00379, C-00380, C-00381, C-00382, C-00383, C-00384, C-00385, C-00386, C-00387, C-00388, C-00389, C-00390, C-00391, C-00392, C-00393, C-00394, C-00395, C-00396, C-00397, C-00398, C-00399, C-00400, C-00401, C-00402, C-00403, C-00404, C-00405, C-00406, C-00407, C-00408, C-00409, C-00410, C-00411, C-00412, C-00413, C-00414, C-00415, C-00416, C-00417, C-00418, C-00419, C-00420, C-00421, C-00422, C-00423, C-00424, C-00425, C-00426, C-00427, C-00428, C-00429, C-00430, C-00431, C-00432, C-00433, C-00434, C-00435, C-00436, C-00437, C-00438, C-00439, C-00440, C-00441, C-00442, C-00443
- survey_results_2009.txt (CH-001): Candidates assigned more than once: C-00008, C-00012, C-00014, C-00017, C-00018, C-00019, C-00020, C-00021, C-00022, C-00026, C-00051, C-00052, C-00068, C-00069, C-00071, C-00072, C-00073, C-00074, C-00079, C-00080, C-00081, C-00087, C-00088, C-00093, C-00094, C-00097, C-00098, C-00099, C-00102, C-00104, C-00106, C-00107, C-00120, C-00125, C-00131, C-00132, C-00133, C-00135, C-00136, C-00137, C-00157, C-00165, C-00168, C-00169, C-00170, C-00177, C-00179, C-00180, C-00184, C-00186, C-00187, C-00193, C-00197, C-00200, C-00201, C-00202, C-00203, C-00204, C-00205, C-00206, C-00210, C-00211, C-00212, C-00213, C-00218, C-00223, C-00224, C-00225, C-00226, C-00227, C-00228, C-00229, C-00230, C-00231, C-00232, C-00233, C-00234, C-00235, C-00236, C-00238, C-00239, C-00240, C-00241, C-00242, C-00243, C-00244, C-00246, C-00247, C-00248],
- survey_results_2009.txt (CH-001): new_findings
- Unaccounted candidates: C-00237, C-00245, C-00250, C-00251, C-00252, C-00253, C-00254, C-00255, C-00256, C-00257, C-00258, C-00259, C-00260, C-00261, C-00262, C-00263, C-00264, C-00265, C-00266, C-00267, C-00268, C-00269, C-00270, C-00271, C-00272, C-00273, C-00274, C-00275, C-00276, C-00277, C-00278, C-00279, C-00280, C-00281, C-00282, C-00283, C-00284, C-00285, C-00286, C-00287, C-00288, C-00289, C-00290, C-00291, C-00292, C-00293, C-00294, C-00295, C-00296, C-00297, C-00298, C-00299, C-00300, C-00301, C-00302, C-00303, C-00304, C-00305, C-00306, C-00307, C-00308, C-00309, C-00310, C-00311, C-00312, C-00313, C-00314, C-00315, C-00316, C-00317, C-00318, C-00319, C-00320, C-00321, C-00322, C-00323, C-00324, C-00325, C-00326, C-00327, C-00328, C-00329, C-00330, C-00331, C-00332, C-00333, C-00334, C-00335, C-00336, C-00337, C-00338, C-00339, C-00340, C-00341, C-00342, C-00343, C-00344, C-00345, C-00346, C-00347, C-00348, C-00349, C-00350, C-00351, C-00352, C-00353, C-00354, C-00355, C-00356, C-00357, C-00358, C-00359, C-00360, C-00361, C-00362, C-00363, C-00364, C-00365, C-00366, C-00367, C-00368, C-00369, C-00370, C-00371, C-00372, C-00373, C-00374, C-00375, C-00376, C-00377, C-00378, C-00379, C-00380, C-00381, C-00382, C-00383, C-00384, C-00385, C-00386, C-00387, C-00388, C-00389, C-00390, C-00391, C-00392, C-00393, C-00394, C-00395, C-00396, C-00397, C-00398, C-00399, C-00400, C-00401, C-00402, C-00403, C-00404, C-00405, C-00406, C-00407, C-00408, C-00409, C-00410, C-00411, C-00412, C-00413, C-00414, C-00415, C-00416, C-00417, C-00418, C-00419, C-00420, C-00421, C-00422, C-00423, C-00424, C-00425, C-00426, C-00427, C-00428, C-00429, C-00430, C-00431, C-00432, C-00433, C-00434, C-00435, C-00436, C-00437, C-00438, C-00439, C-00440, C-00441, C-00442, C-00443, C-00444, C-00445, C-00446, C-00447, C-00448, C-00449, C-00450, C-00451, C-00452, C-00453, C-00454, C-00455, C-00456, C-00457, C-00458, C-00459, C-00460, C-00461, C-00462, C-00463, C-00464, C-00465, C-00466, C-00467, C-00468, C-00469, C-00470, C-00471, C-00472, C-00473, C-00474, C-00475, C-00476, C-00477, C-00478, C-00479, C-00480, C-00481, C-00482, C-00483, C-00484, C-00485, C-00486, C-00487, C-00488, C-00489, C-00490, C-00491, C-00492, C-00493, C-00494, C-00495, C-00496, C-00497, C-00498, C-00499, C-00500, C-00501, C-00502, C-00503, C-00504, C-00505, C-00506, C-00507, C-00508, C-00509, C-00510, C-00511, C-00512, C-00513, C-00514, C-00515, C-00516, C-00517, C-00518, C-00519, C-00520, C-00521, C-00522, C-00523, C-00524, C-00525, C-00526, C-00527, C-00528, C-00529, C-00530, C-00531, C-00532, C-00533, C-00534, C-00535, C-00536, C-00537, C-00538, C-00539, C-00540, C-00541, C-00542, C-00543, C-00544, C-00545, C-00546, C-00547, C-00548, C-00549, C-00550, C-00551, C-00552, C-00553, C-00554, C-00555, C-00556, C-00557, C-00558, C-00559, C-00560, C-00561, C-00562, C-00563, C-00564, C-00565, C-00566, C-00567, C-00568, C-00569, C-00570, C-00571, C-00572, C-00573, C-00574, C-00575, C-00576, C-00577, C-00578, C-00579, C-00580, C-00581, C-00582, C-00583, C-00584, C-00585, C-00586, C-00587, C-00588, C-00589, C-00590, C-00591, C-00592, C-00593, C-00594, C-00595, C-00596, C-00597, C-00598, C-00599, C-00600, C-00601, C-00602
- C-00019 (conversations/conv_pines018_item_transfer.eml, CH-001): no verified quote; check the candidate against the source.
- C-00021 (conversations/conv_pines018_item_transfer.eml, CH-001): no verified quote; check the candidate against the source.
- C-00023 (conversations/conv_pines018_item_transfer.eml, CH-001): no verified quote; check the candidate against the source.
- C-00026 (conversations/conv_pines018_item_transfer.eml, CH-001): no verified quote; check the candidate against the source.
- C-00028 (conversations/conv_pines019_020_missing_intransit.eml, CH-001): no verified quote; check the candidate against the source.
- C-00033 (conversations/conv_pines022_deletions.eml, CH-001): no verified quote; check the candidate against the source.
- C-00035 (conversations/conv_pines022_deletions.eml, CH-001): no verified quote; check the candidate against the source.
- C-00047 (conversations/conv_pines024_inactive_patrons.eml, CH-001): no verified quote; check the candidate against the source.
- C-00051 (conversations/conv_pines024_inactive_patrons.eml, CH-001): no verified quote; check the candidate against the source.
- C-00052 (conversations/conv_pines024_inactive_patrons.eml, CH-001): no verified quote; check the candidate against the source.
- C-00085 (early_draft_srs_galecia.txt, CH-003): no verified quote; check the candidate against the source.
- C-00098 (email_report_features.eml, CH-001): no verified quote; check the candidate against the source.
- C-00101 (email_staff_login.eml, CH-001): no verified quote; check the candidate against the source.
- C-00102 (email_staff_login.eml, CH-001): no verified quote; check the candidate against the source.
- C-00105 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00106 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00108 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00109 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00113 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00115 (interview_cataloging_2009-05-08.txt, CH-001): no verified quote; check the candidate against the source.
- C-00117 (interview_cataloging_2009-05-08.txt, CH-001): no verified quote; check the candidate against the source.
- C-00118 (interview_cataloging_2009-05-08.txt, CH-001): no verified quote; check the candidate against the source.
- C-00120 (interview_cataloging_2009-05-08.txt, CH-001): no verified quote; check the candidate against the source.
- C-00128 (interview_sysadmin_2009-05-10.txt, CH-001): no verified quote; check the candidate against the source.
- C-00132 (interview_sysadmin_2009-05-10.txt, CH-001): no verified quote; check the candidate against the source.
- C-00133 (interview_sysadmin_2009-05-10.txt, CH-001): no verified quote; check the candidate against the source.
- C-00156 (meeting_tech_subcommittee_2009-06-30.txt, CH-001): no verified quote; check the candidate against the source.
- C-00169 (conversations/conv_pines014_material_volume.eml, CH-001): no verified quote; check the candidate against the source.
- C-00170 (conversations/conv_pines014_material_volume.eml, CH-001): no verified quote; check the candidate against the source.
- C-00171 (conversations/conv_pines014_material_volume.eml, CH-001): no verified quote; check the candidate against the source.
- C-00172 (conversations/conv_pines015_capacity_interface.eml, CH-001): no verified quote; check the candidate against the source.
- C-00173 (conversations/conv_pines015_capacity_interface.eml, CH-001): no verified quote; check the candidate against the source.
- C-00174 (conversations/conv_pines015_capacity_interface.eml, CH-001): no verified quote; check the candidate against the source.
- C-00175 (conversations/conv_pines015_capacity_interface.eml, CH-001): no verified quote; check the candidate against the source.
- C-00176 (conversations/conv_pines015_capacity_interface.eml, CH-001): no verified quote; check the candidate against the source.
- C-00177 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00178 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00179 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00180 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00181 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00182 (conversations/conv_pines019_020_missing_intransit.eml, CH-001): no verified quote; check the candidate against the source.
- C-00183 (conversations/conv_pines019_020_missing_intransit.eml, CH-001): no verified quote; check the candidate against the source.
- C-00184 (conversations/conv_pines019_020_missing_intransit.eml, CH-001): no verified quote; check the candidate against the source.
- C-00185 (conversations/conv_pines019_020_missing_intransit.eml, CH-001): no verified quote; check the candidate against the source.
- C-00187 (conversations/conv_pines022_deletions.eml, CH-001): no verified quote; check the candidate against the source.
- C-00188 (conversations/conv_pines022_deletions.eml, CH-001): no verified quote; check the candidate against the source.
- C-00189 (conversations/conv_pines022_deletions.eml, CH-001): no verified quote; check the candidate against the source.
- C-00190 (conversations/conv_pines022_deletions.eml, CH-001): no verified quote; check the candidate against the source.
- C-00191 (conversations/conv_pines023_patron_characteristics.eml, CH-001): no verified quote; check the candidate against the source.
- C-00192 (conversations/conv_pines024_inactive_patrons.eml, CH-001): no verified quote; check the candidate against the source.
- C-00193 (conversations/conv_pines024_inactive_patrons.eml, CH-001): no verified quote; check the candidate against the source.
- C-00194 (conversations/conv_pines024_inactive_patrons.eml, CH-001): no verified quote; check the candidate against the source.
- C-00195 (conversations/conv_pines024_inactive_patrons.eml, CH-001): no verified quote; check the candidate against the source.
- C-00196 (conversations/conv_pines024_inactive_patrons.eml, CH-001): no verified quote; check the candidate against the source.
- C-00197 (conversations/conv_pines024_inactive_patrons.eml, CH-001): no verified quote; check the candidate against the source.
- C-00198 (conversations/conv_pines024_inactive_patrons.eml, CH-001): no verified quote; check the candidate against the source.
- C-00199 (conversations/conv_pines024_inactive_patrons.eml, CH-001): no verified quote; check the candidate against the source.
- C-00200 (early_draft_srs_galecia.txt, CH-001): no verified quote; check the candidate against the source.
- C-00202 (early_draft_srs_galecia.txt, CH-002): no verified quote; check the candidate against the source.
- C-00203 (early_draft_srs_galecia.txt, CH-003): no verified quote; check the candidate against the source.
- C-00204 (early_draft_srs_galecia.txt, CH-003): no verified quote; check the candidate against the source.
- C-00209 (email_report_features.eml, CH-001): no verified quote; check the candidate against the source.
- C-00210 (email_report_features.eml, CH-001): no verified quote; check the candidate against the source.
- C-00211 (email_report_features.eml, CH-001): no verified quote; check the candidate against the source.
- C-00212 (email_report_features.eml, CH-001): no verified quote; check the candidate against the source.
- C-00213 (email_report_features.eml, CH-001): no verified quote; check the candidate against the source.
- C-00214 (email_report_features.eml, CH-001): no verified quote; check the candidate against the source.
- C-00215 (email_report_features.eml, CH-001): no verified quote; check the candidate against the source.
- C-00216 (email_report_features.eml, CH-001): no verified quote; check the candidate against the source.
- C-00217 (email_report_features.eml, CH-001): no verified quote; check the candidate against the source.
- C-00218 (email_report_features.eml, CH-001): no verified quote; check the candidate against the source.
- C-00219 (email_staff_login.eml, CH-001): no verified quote; check the candidate against the source.
- C-00220 (email_staff_login.eml, CH-001): no verified quote; check the candidate against the source.
- C-00221 (email_staff_login.eml, CH-001): no verified quote; check the candidate against the source.
- C-00222 (email_staff_login.eml, CH-001): no verified quote; check the candidate against the source.
- C-00223 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00224 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00225 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00226 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00227 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00228 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00229 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00230 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00231 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00232 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00233 (interview_sysadmin_2009-05-10.txt, CH-001): no verified quote; check the candidate against the source.
- C-00234 (interview_sysadmin_2009-05-10.txt, CH-001): no verified quote; check the candidate against the source.
- C-00235 (interview_sysadmin_2009-05-10.txt, CH-001): no verified quote; check the candidate against the source.
- C-00236 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00237 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00238 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00239 (meeting_minutes/meeting_2009-07-20_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00240 (meeting_minutes/meeting_2009-07-20_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00241 (meeting_tech_subcommittee_2009-06-30.txt, CH-001): no verified quote; check the candidate against the source.
- C-00242 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00243 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00244 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00245 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00246 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00247 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00248 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00249 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00251 (conversations/conv_pines014_material_volume.eml, CH-001): no verified quote; check the candidate against the source.
- C-00252 (conversations/conv_pines014_material_volume.eml, CH-001): no verified quote; check the candidate against the source.
- C-00253 (conversations/conv_pines014_material_volume.eml, CH-001): no verified quote; check the candidate against the source.
- C-00254 (conversations/conv_pines014_material_volume.eml, CH-001): no verified quote; check the candidate against the source.
- C-00255 (conversations/conv_pines014_material_volume.eml, CH-001): no verified quote; check the candidate against the source.
- C-00256 (conversations/conv_pines014_material_volume.eml, CH-001): no verified quote; check the candidate against the source.
- C-00257 (conversations/conv_pines014_material_volume.eml, CH-001): no verified quote; check the candidate against the source.
- C-00258 (conversations/conv_pines014_material_volume.eml, CH-001): no verified quote; check the candidate against the source.
- C-00259 (conversations/conv_pines014_material_volume.eml, CH-001): no verified quote; check the candidate against the source.
- C-00260 (conversations/conv_pines014_material_volume.eml, CH-001): no verified quote; check the candidate against the source.
- C-00261 (conversations/conv_pines014_material_volume.eml, CH-001): no verified quote; check the candidate against the source.
- C-00262 (conversations/conv_pines014_material_volume.eml, CH-001): no verified quote; check the candidate against the source.
- C-00263 (conversations/conv_pines014_material_volume.eml, CH-001): no verified quote; check the candidate against the source.
- C-00264 (conversations/conv_pines014_material_volume.eml, CH-001): no verified quote; check the candidate against the source.
- C-00265 (conversations/conv_pines014_material_volume.eml, CH-001): no verified quote; check the candidate against the source.
- C-00266 (conversations/conv_pines014_material_volume.eml, CH-001): no verified quote; check the candidate against the source.
- C-00267 (conversations/conv_pines014_material_volume.eml, CH-001): no verified quote; check the candidate against the source.
- C-00268 (conversations/conv_pines014_material_volume.eml, CH-001): no verified quote; check the candidate against the source.
- C-00269 (conversations/conv_pines014_material_volume.eml, CH-001): no verified quote; check the candidate against the source.
- C-00270 (conversations/conv_pines015_capacity_interface.eml, CH-001): no verified quote; check the candidate against the source.
- C-00271 (conversations/conv_pines015_capacity_interface.eml, CH-001): no verified quote; check the candidate against the source.
- C-00272 (conversations/conv_pines015_capacity_interface.eml, CH-001): no verified quote; check the candidate against the source.
- C-00273 (conversations/conv_pines015_capacity_interface.eml, CH-001): no verified quote; check the candidate against the source.
- C-00274 (conversations/conv_pines015_capacity_interface.eml, CH-001): no verified quote; check the candidate against the source.
- C-00276 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00277 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00278 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00279 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00280 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00281 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00282 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00283 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00284 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00285 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00286 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00287 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00288 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00289 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00290 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00291 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00292 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00293 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00294 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00295 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00296 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00297 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00298 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00299 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00300 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00301 (conversations/conv_pines018_item_transfer.eml, CH-001): no verified quote; check the candidate against the source.
- C-00302 (conversations/conv_pines018_item_transfer.eml, CH-001): no verified quote; check the candidate against the source.
- C-00303 (conversations/conv_pines018_item_transfer.eml, CH-001): no verified quote; check the candidate against the source.
- C-00304 (conversations/conv_pines018_item_transfer.eml, CH-001): no verified quote; check the candidate against the source.
- C-00305 (conversations/conv_pines018_item_transfer.eml, CH-001): no verified quote; check the candidate against the source.
- C-00306 (conversations/conv_pines018_item_transfer.eml, CH-001): no verified quote; check the candidate against the source.
- C-00307 (conversations/conv_pines018_item_transfer.eml, CH-001): no verified quote; check the candidate against the source.
- C-00308 (conversations/conv_pines018_item_transfer.eml, CH-001): no verified quote; check the candidate against the source.
- C-00309 (conversations/conv_pines018_item_transfer.eml, CH-001): no verified quote; check the candidate against the source.
- C-00310 (conversations/conv_pines018_item_transfer.eml, CH-001): no verified quote; check the candidate against the source.
- C-00311 (conversations/conv_pines019_020_missing_intransit.eml, CH-001): no verified quote; check the candidate against the source.
- C-00312 (conversations/conv_pines019_020_missing_intransit.eml, CH-001): no verified quote; check the candidate against the source.
- C-00313 (conversations/conv_pines019_020_missing_intransit.eml, CH-001): no verified quote; check the candidate against the source.
- C-00314 (conversations/conv_pines019_020_missing_intransit.eml, CH-001): no verified quote; check the candidate against the source.
- C-00315 (conversations/conv_pines019_020_missing_intransit.eml, CH-001): no verified quote; check the candidate against the source.
- C-00316 (conversations/conv_pines019_020_missing_intransit.eml, CH-001): no verified quote; check the candidate against the source.
- C-00317 (conversations/conv_pines019_020_missing_intransit.eml, CH-001): no verified quote; check the candidate against the source.
- C-00318 (conversations/conv_pines019_020_missing_intransit.eml, CH-001): no verified quote; check the candidate against the source.
- C-00319 (conversations/conv_pines019_020_missing_intransit.eml, CH-001): no verified quote; check the candidate against the source.
- C-00320 (conversations/conv_pines019_020_missing_intransit.eml, CH-001): no verified quote; check the candidate against the source.
- C-00321 (conversations/conv_pines019_020_missing_intransit.eml, CH-001): no verified quote; check the candidate against the source.
- C-00322 (conversations/conv_pines019_020_missing_intransit.eml, CH-001): no verified quote; check the candidate against the source.
- C-00323 (conversations/conv_pines019_020_missing_intransit.eml, CH-001): no verified quote; check the candidate against the source.
- C-00324 (conversations/conv_pines019_020_missing_intransit.eml, CH-001): no verified quote; check the candidate against the source.
- C-00325 (conversations/conv_pines021_item_purging.eml, CH-001): no verified quote; check the candidate against the source.
- C-00326 (conversations/conv_pines022_deletions.eml, CH-001): no verified quote; check the candidate against the source.
- C-00327 (conversations/conv_pines022_deletions.eml, CH-001): no verified quote; check the candidate against the source.
- C-00328 (conversations/conv_pines022_deletions.eml, CH-001): no verified quote; check the candidate against the source.
- C-00329 (conversations/conv_pines022_deletions.eml, CH-001): no verified quote; check the candidate against the source.
- C-00330 (conversations/conv_pines022_deletions.eml, CH-001): no verified quote; check the candidate against the source.
- C-00331 (conversations/conv_pines022_deletions.eml, CH-001): no verified quote; check the candidate against the source.
- C-00332 (conversations/conv_pines022_deletions.eml, CH-001): no verified quote; check the candidate against the source.
- C-00333 (conversations/conv_pines022_deletions.eml, CH-001): no verified quote; check the candidate against the source.
- C-00334 (conversations/conv_pines022_deletions.eml, CH-001): no verified quote; check the candidate against the source.
- C-00335 (conversations/conv_pines023_patron_characteristics.eml, CH-001): no verified quote; check the candidate against the source.
- C-00336 (conversations/conv_pines023_patron_characteristics.eml, CH-001): no verified quote; check the candidate against the source.
- C-00337 (conversations/conv_pines023_patron_characteristics.eml, CH-001): no verified quote; check the candidate against the source.
- C-00338 (conversations/conv_pines023_patron_characteristics.eml, CH-001): no verified quote; check the candidate against the source.
- C-00339 (conversations/conv_pines023_patron_characteristics.eml, CH-001): no verified quote; check the candidate against the source.
- C-00340 (conversations/conv_pines023_patron_characteristics.eml, CH-001): no verified quote; check the candidate against the source.
- C-00341 (conversations/conv_pines023_patron_characteristics.eml, CH-001): no verified quote; check the candidate against the source.
- C-00342 (conversations/conv_pines023_patron_characteristics.eml, CH-001): no verified quote; check the candidate against the source.
- C-00343 (conversations/conv_pines023_patron_characteristics.eml, CH-001): no verified quote; check the candidate against the source.
- C-00344 (conversations/conv_pines024_inactive_patrons.eml, CH-001): no verified quote; check the candidate against the source.
- C-00345 (conversations/conv_pines024_inactive_patrons.eml, CH-001): no verified quote; check the candidate against the source.
- C-00346 (conversations/conv_pines024_inactive_patrons.eml, CH-001): no verified quote; check the candidate against the source.
- C-00347 (conversations/conv_pines024_inactive_patrons.eml, CH-001): no verified quote; check the candidate against the source.
- C-00348 (conversations/conv_pines024_inactive_patrons.eml, CH-001): no verified quote; check the candidate against the source.
- C-00349 (conversations/conv_pines024_inactive_patrons.eml, CH-001): no verified quote; check the candidate against the source.
- C-00350 (early_draft_srs_galecia.txt, CH-001): no verified quote; check the candidate against the source.
- C-00351 (early_draft_srs_galecia.txt, CH-001): no verified quote; check the candidate against the source.
- C-00352 (early_draft_srs_galecia.txt, CH-001): no verified quote; check the candidate against the source.
- C-00353 (early_draft_srs_galecia.txt, CH-001): no verified quote; check the candidate against the source.
- C-00354 (early_draft_srs_galecia.txt, CH-001): no verified quote; check the candidate against the source.
- C-00355 (early_draft_srs_galecia.txt, CH-001): no verified quote; check the candidate against the source.
- C-00356 (early_draft_srs_galecia.txt, CH-001): no verified quote; check the candidate against the source.
- C-00357 (early_draft_srs_galecia.txt, CH-001): no verified quote; check the candidate against the source.
- C-00358 (early_draft_srs_galecia.txt, CH-001): no verified quote; check the candidate against the source.
- C-00359 (early_draft_srs_galecia.txt, CH-002): no verified quote; check the candidate against the source.
- C-00360 (early_draft_srs_galecia.txt, CH-002): no verified quote; check the candidate against the source.
- C-00361 (early_draft_srs_galecia.txt, CH-002): no verified quote; check the candidate against the source.
- C-00362 (early_draft_srs_galecia.txt, CH-002): no verified quote; check the candidate against the source.
- C-00363 (early_draft_srs_galecia.txt, CH-002): no verified quote; check the candidate against the source.
- C-00364 (early_draft_srs_galecia.txt, CH-002): no verified quote; check the candidate against the source.
- C-00365 (email_financial_reports.eml, CH-001): no verified quote; check the candidate against the source.
- C-00366 (email_financial_reports.eml, CH-001): no verified quote; check the candidate against the source.
- C-00369 (email_staff_login.eml, CH-001): no verified quote; check the candidate against the source.
- C-00370 (email_staff_login.eml, CH-001): no verified quote; check the candidate against the source.
- C-00371 (email_staff_login.eml, CH-001): no verified quote; check the candidate against the source.
- C-00372 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00373 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00374 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00375 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00376 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00377 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00378 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00379 (interview_cataloging_2009-05-08.txt, CH-001): no verified quote; check the candidate against the source.
- C-00380 (interview_cataloging_2009-05-08.txt, CH-001): no verified quote; check the candidate against the source.
- C-00381 (interview_cataloging_2009-05-08.txt, CH-001): no verified quote; check the candidate against the source.
- C-00382 (interview_cataloging_2009-05-08.txt, CH-001): no verified quote; check the candidate against the source.
- C-00383 (interview_cataloging_2009-05-08.txt, CH-001): no verified quote; check the candidate against the source.
- C-00384 (interview_cataloging_2009-05-08.txt, CH-001): no verified quote; check the candidate against the source.
- C-00385 (interview_sysadmin_2009-05-10.txt, CH-001): no verified quote; check the candidate against the source.
- C-00387 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00388 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00389 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00390 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00391 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00392 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00393 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00394 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00395 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00396 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00397 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00398 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00399 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00400 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00401 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00402 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00403 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00404 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00405 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00406 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00407 (meeting_minutes/meeting_2009-07-20_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00408 (meeting_minutes/meeting_2009-07-20_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00409 (meeting_minutes/meeting_2009-07-20_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00410 (meeting_minutes/meeting_2009-07-20_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00411 (meeting_tech_subcommittee_2009-06-30.txt, CH-001): no verified quote; check the candidate against the source.
- C-00421 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00422 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00424 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00425 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00426 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00427 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00428 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00429 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00430 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00431 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00432 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00433 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00434 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00435 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00436 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00437 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00438 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00439 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00440 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00441 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00442 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00443 (survey_results_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00457 (conversations/conv_pines015_capacity_interface.eml, CH-001): no verified quote; check the candidate against the source.
- C-00458 (conversations/conv_pines015_capacity_interface.eml, CH-001): no verified quote; check the candidate against the source.
- C-00459 (conversations/conv_pines015_capacity_interface.eml, CH-001): no verified quote; check the candidate against the source.
- C-00460 (conversations/conv_pines015_capacity_interface.eml, CH-001): no verified quote; check the candidate against the source.
- C-00461 (conversations/conv_pines015_capacity_interface.eml, CH-001): no verified quote; check the candidate against the source.
- C-00462 (conversations/conv_pines015_capacity_interface.eml, CH-001): no verified quote; check the candidate against the source.
- C-00463 (conversations/conv_pines015_capacity_interface.eml, CH-001): no verified quote; check the candidate against the source.
- C-00464 (conversations/conv_pines015_capacity_interface.eml, CH-001): no verified quote; check the candidate against the source.
- C-00465 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00466 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00467 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00468 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00469 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00470 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00471 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00472 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00473 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00474 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00475 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00476 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00477 (conversations/conv_pines016_shelf_space.eml, CH-001): no verified quote; check the candidate against the source.
- C-00478 (conversations/conv_pines018_item_transfer.eml, CH-001): no verified quote; check the candidate against the source.
- C-00479 (conversations/conv_pines018_item_transfer.eml, CH-001): no verified quote; check the candidate against the source.
- C-00480 (conversations/conv_pines018_item_transfer.eml, CH-001): no verified quote; check the candidate against the source.
- C-00481 (conversations/conv_pines018_item_transfer.eml, CH-001): no verified quote; check the candidate against the source.
- C-00482 (conversations/conv_pines019_020_missing_intransit.eml, CH-001): no verified quote; check the candidate against the source.
- C-00484 (conversations/conv_pines021_item_purging.eml, CH-001): no verified quote; check the candidate against the source.
- C-00500 (conversations/conv_pines023_patron_characteristics.eml, CH-001): no verified quote; check the candidate against the source.
- C-00515 (conversations/conv_pines024_inactive_patrons.eml, CH-001): no verified quote; check the candidate against the source.
- C-00516 (conversations/conv_pines024_inactive_patrons.eml, CH-001): no verified quote; check the candidate against the source.
- C-00517 (conversations/conv_pines024_inactive_patrons.eml, CH-001): no verified quote; check the candidate against the source.
- C-00526 (early_draft_srs_galecia.txt, CH-001): no verified quote; check the candidate against the source.
- C-00527 (early_draft_srs_galecia.txt, CH-001): no verified quote; check the candidate against the source.
- C-00528 (early_draft_srs_galecia.txt, CH-001): no verified quote; check the candidate against the source.
- C-00529 (early_draft_srs_galecia.txt, CH-002): no verified quote; check the candidate against the source.
- C-00530 (early_draft_srs_galecia.txt, CH-002): no verified quote; check the candidate against the source.
- C-00531 (email_financial_reports.eml, CH-001): no verified quote; check the candidate against the source.
- C-00533 (email_financial_reports.eml, CH-001): no verified quote; check the candidate against the source.
- C-00561 (email_staff_login.eml, CH-001): no verified quote; check the candidate against the source.
- C-00562 (email_staff_login.eml, CH-001): no verified quote; check the candidate against the source.
- C-00563 (email_staff_login.eml, CH-001): no verified quote; check the candidate against the source.
- C-00564 (email_staff_login.eml, CH-001): no verified quote; check the candidate against the source.
- C-00565 (email_staff_login.eml, CH-001): no verified quote; check the candidate against the source.
- C-00566 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00567 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00568 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00569 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00570 (evergreen_reference_2009.txt, CH-001): no verified quote; check the candidate against the source.
- C-00571 (interview_cataloging_2009-05-08.txt, CH-001): no verified quote; check the candidate against the source.
- C-00586 (interview_sysadmin_2009-05-10.txt, CH-001): no verified quote; check the candidate against the source.
- C-00587 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00588 (meeting_minutes/meeting_2009-03-15_minutes.txt, CH-001): no verified quote; check the candidate against the source.
- C-00601 (meeting_tech_subcommittee_2009-06-30.txt, CH-001): no verified quote; check the candidate against the source.
- C-00602 (meeting_tech_subcommittee_2009-06-30.txt, CH-001): no verified quote; check the candidate against the source.

## Source manifest

- `conversations/conv_pines014_material_volume.eml` — SHA-256: `67e2f8c1759950c7f16131e37a4ed9826e2faa39955ae466c92bfd2067686533`
- `conversations/conv_pines015_capacity_interface.eml` — SHA-256: `b6f80a4fa4814bd0e09aaea06bae0e1c902012d5c44b181cb71d70f3b1be6c5f`
- `conversations/conv_pines016_shelf_space.eml` — SHA-256: `f48b2e6a187e56b2b849fc98c4719067074658540a8a2687c82f0b875fb2ed96`
- `conversations/conv_pines018_item_transfer.eml` — SHA-256: `09032a8623291e8aca003b1a8da44c433174744fd9259e9304e4f865690022c6`
- `conversations/conv_pines019_020_missing_intransit.eml` — SHA-256: `41f2338bc47a114ca48a914de73e1386e4871818dfd776df1d2d866e82f5413d`
- `conversations/conv_pines021_item_purging.eml` — SHA-256: `10a211d5307d896251c3e54321a684844bf2d9bdb92ff271a624bb0713919b2f`
- `conversations/conv_pines022_deletions.eml` — SHA-256: `498e55130227b3602c4c6687bf6f5744a17b70916866fa9ff34dce044f04c3da`
- `conversations/conv_pines023_patron_characteristics.eml` — SHA-256: `aac5024f566527948e6a250932bcdf8559346785e7717f6616a0ccd0c1de0e3c`
- `conversations/conv_pines024_inactive_patrons.eml` — SHA-256: `fbfb46edaec8b7e1acf085437c1e758e4bf2e3bc6033a0940004be2aef849d04`
- `early_draft_srs_galecia.txt` — SHA-256: `47082bac52d37617791e5ade8579e0217b8f122017750fbd8c03863dbe3d3e1a`
- `email_financial_reports.eml` — SHA-256: `167352844ff7f34abbe3dd7a041b1b383f2baa82d5ee54563492b1e3a134f98e`
- `email_report_features.eml` — SHA-256: `eb1da67dbdfb8f5f7cd17fe3e10af69a271d5cfa6c45f44f5f015b44f71ee706`
- `email_staff_login.eml` — SHA-256: `f93eb5c328a5b5df493acb452b9e9b822db5388367377e3f534cbfaa4a42d5ab`
- `evergreen_reference_2009.txt` — SHA-256: `a276ba86428801b6029689a36733f2946c3b9e00b760a33826419dd7c271bf03`
- `interview_cataloging_2009-05-08.txt` — SHA-256: `b51f15098ce470aa1b16fd22e009479bf5bc4a8ca087a44bb4587392ca9560ca`
- `interview_sysadmin_2009-05-10.txt` — SHA-256: `0588270c747c4ac937a73efb8f5446090b67e66c844e5a679a259d58ec56d855`
- `meeting_minutes/meeting_2009-03-15_minutes.txt` — SHA-256: `9ac3ed36fe8d6c7d47727d3a788339405241aa10ae23b5e057af0ffc3c456eb0`
- `meeting_minutes/meeting_2009-07-20_minutes.txt` — SHA-256: `324bedcf93362dbdcfc2120c90f3c51f707b32231ac1322d0526ae90fc3afff7`
- `meeting_tech_subcommittee_2009-06-30.txt` — SHA-256: `d8cb6fcd4b39082e58c35424f5a50f9118c6c0e0f2c566fbc28598936c3decb6`
- `survey_results_2009.txt` — SHA-256: `a624f32c64391c47e6038bb1a55ab4dd15780631ae64ee61932b6d4d24c7a526`

## Evidence ledger

### C-00001: Library Material Volume Report Capabilities

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.

> The system should provide the ability to report on the volume of material
> in a given library at any point in time, based on:
> - New acquisitions
> - Items on the shelf (checked in)
> - Items out in circulation (checked out)
> 
> The report should allow breaking down volume in categories such as:
> - Total items in library
> - Number of holds
> - Number of adult fiction
> - Number of board books
> - Other customizable categories

### C-00002: High-Level Summary View of Branch Capacities

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.

> This reminds me of the capacity interface from the King County spec. It
> was basically a dashboard showing all libraries' capacity at once.

### C-00003: Drill-Down Functionality for Individual Branches

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.

> Ability to drill down into individual branches

### C-00004: Filtering and Sorting Capabilities

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.

> Sorting and filtering capabilities (region, type, load)

### C-00005: Trend Data Display for Capacity Changes Over Time

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.

> show trends? Like, is
> this branch growing or shrinking? That helps with long-term planning.

### C-00006: Export Functionality to CSV Format

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.

> And export to CSV for the directors who want spreadsheets.

### C-00007: Shelf Space Utilization Report Features

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.

> This is the "shelf space report" we've been talking about. The idea is:
> for each genre and format of material, compare:
> 1. Percentage of total circulations
> 2. Percentage of the collection
> 3. Percentage of total shelf space
> 
> The report should be able to run per library and per system. This way branch
> managers can see their local situation AND see how they compare to the system
> average.

### C-00008: Data Estimation for Shelf Space Calculation

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.

> The tricky part is #3. Shelf space isn't directly tracked in the database.
> We'd need to estimate based on item dimensions or use item count as a proxy.

### C-00009: Multi-level and comparative reporting capabilities

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.

> Our directors review
> this data quarterly and need both views.
> 
> Also, can we include a "comparison" view that shows each library's breakdown
> side by side?

### C-00010: Filtering Capabilities by Date Range

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.

> Can we also filter by date range? Like, what was the shelf space utilization
> in Q1 vs. Q2? Seasons matter for our collection.

### C-00011: System-Level Data Support

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.

> I would need this at the system level for sure. When I look at Twin Lakes
> as a whole, we might have too many romance novels in some branches and not
> enough in others.

### C-00012: Estimate Shelf Space from Existing Data

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.

> Robert will investigate how to estimate shelf space from existing data

### C-00013: Query Builder for Candidate Material Selection

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.

> Query builder for candidate selection - we can reuse the report query
>    tool for this.

### C-00014: Ability to Save and Reuse Queries

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.

> Save/share queries - similar to report templates.

### C-00015: Manual Selection of Items from Query Results

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.

> I also want to be able to MANUALLY SELECT from query results.

### C-00016: Change Item Location Records

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.

> Change records of selected items to new location

### C-00017: Generate Pull Lists and Transit Labels

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.

> Pull list generation - create a printable list of items to be moved.

### C-00018: Revert Items to Original Location After a Set Period

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.

> Revert items to original location after a set period of time

### C-00019: Support for Time-Based and Event-Based Auto Revert

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00020: Scheduled Task to Revert Items Based on Criteria

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.

> a scheduled task that checks transferred items
>    and reverts them based on time or status criteria.

### C-00021: Logging of Transfer Activities

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00022: Permission Control for Transfer Operations

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.

> This should be limited
> to certain roles (managers, administrators, transfer coordinators).

### C-00023: Preview of Changes Before Execution

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00024: Undo Function for Transfer Actions

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.

> And we need an undo function! What if someone clicks the wrong button?

### C-00025: Transfer Delay Alerts and Notifications

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.

> set up alerts? If an item transfer is delayed or has issues,
> notify me.

### C-00026: Track Transfer History per Item

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00027: Missing and Damaged Items Report

Source: `conversations/conv_pines019_020_missing_intransit.eml`, chunk `CH-001`.

> System provides reports of missing and damaged items per branch.

### C-00028: In-Transit Items Report

Source: `conversations/conv_pines019_020_missing_intransit.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00029: Item purging utility with customizable criteria

Source: `conversations/conv_pines021_item_purging.eml`, chunk `CH-001`.

> The system should provide a utility and reports for identifying item records
> to purge, based on customizable criteria such as:
> - An item has been in status "missing" for more than X months
> - An item has status "discard/weed"
> 
> The system should:
> - Provide a report to assist in the conversion of items from one status to
>   another
> - Provide a last copy report singling out a library system's last copies,
>   to assist catalogers who need to edit WorldCat entries
> - Provide a quick effective method for deleting volume entries along with
>   copy entries, as well as records with no items attached
> 
> Safety measures:
> - Read-only reports for identifying candidates
> - Separate confirmation step for actual deletions
> - Audit trail for all purges

### C-00030: Audit Log for Record Deletions

Source: `conversations/conv_pines022_deletions.eml`, chunk `CH-001`.

> This is actually a good idea from an auditing standpoint. Currently,
> Evergreen does not log deletions - once something is deleted, it's gone.
> 
> To implement this, we'd need:
> 1. A trigger in the database that logs deletions to an audit table
> 2. Fields: record_type, record_id, deleted_by, deleted_at, location
> 3. A report interface to query this audit table

### C-00031: Database Trigger for Deletion Logging

Source: `conversations/conv_pines022_deletions.eml`, chunk `CH-001`.

> To implement this, we'd need:
> 1. A trigger in the database that logs deletions to an audit table
> 2. Fields: record_type, record_id, deleted_by, deleted_at, location

### C-00032: Deletion Audit Report Interface

Source: `conversations/conv_pines022_deletions.eml`, chunk `CH-001`.

> A report interface to query this audit table
> 
> The report should show deletions per location and per system. We can
> aggregate by date range, by user, by record type.

### C-00033: Count and Track Record Deletions

Source: `conversations/conv_pines022_deletions.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00034: Track Deletions by Record Type

Source: `conversations/conv_pines022_deletions.eml`, chunk `CH-001`.

> - Deletions by type (item vs patron vs other)

### C-00035: Track Deletions by User and Location

Source: `conversations/conv_pines022_deletions.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00036: Track and Report Denied Deletions

Source: `conversations/conv_pines022_deletions.eml`, chunk `CH-001`.

> Can we also track attempted deletions that were denied? That would tell
> us if someone is trying to delete things they shouldn't.

### C-00037: Support for filtering patron data by characteristics

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.

> I need to be able to both LIMIT and GROUP BY patron characteristics.
> For example:
> - Limit: Show me only patrons in zip code 30501
> - Group By: Show me checkout counts grouped by age range

### C-00038: Support for grouping patron data by characteristics

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.

> Can we also GROUP BY these fields? Like, show me circulation by age range,
> or patron count by home branch?

### C-00039: Configurable age ranges in reports

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.

> The age ranges need to be configurable too. Like, 0-5, 6-10, 11-15, etc.

### C-00040: Inclusion of null or missing data in reports

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.

> The "age range" is calculated from the birth_date field, which means we
> need to compute it at query time. We can create age brackets in the query.
> 
> Combining filters is also doable - just add WHERE clauses. We can support
> both AND and OR logic.
> 
> One consideration: if patrons haven't provided optional fields, they'll
> show up as null. We should include them in the report (with null values)
> rather than excluding them, because excluding data silently can lead to
> misleading results.

### C-00041: Support for calculating derived fields such as age range

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.

> The "age range" is calculated from the birth_date field, which means we
> need to compute it at query time.

### C-00042: Technical feasibility of requested features

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.

> From a technical standpoint, these queries are straightforward. All the
> fields mentioned (age range, zip code, county, home branch, patron type,
> preferred language) exist in the patron table.

### C-00043: Support for logical combination of filters

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.

> Combining filters is also doable - just add WHERE clauses. We can support
> both AND and OR logic.

### C-00044: Support for multiple patron characteristics in one report

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.

> Can we combine demographic filters? Like "show me all Juvenile patrons in
> zip code 30505 who haven't checked anything out in 6 months"?

### C-00045: Configurable inactivity threshold (X days)

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.

> X should be configurable - we usually use 365
> days but it would be nice to adjust.

### C-00046: Configurable report levels - System, Home Library, County

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.

> The list should be configurable to different levels - System, Home Library,
> County, etc.

### C-00047: Inclusion of electronic activity in report

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00048: Tracking electronic activity through multiple data sources

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.

> we track:
> - OPAC login events
> - Online hold placements
> - Online renewals
> - Digital resource access (if logged)
> 
> These are stored in different tables, so we'd need a combined query.

### C-00049: Exclusion of certain patrons from report

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.

> we should be able to EXCLUDE certain patrons from the
> inactive report. For example:
> - Patrons with "do not disturb" flags
> - VIP patrons
> - Staff members
> - Patrons who have opted out of communications

### C-00050: Inclusion of current mailing addresses in report for outreach

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.

> the report needs to
> include current mailing addresses.

### C-00051: Support for exporting the report in CSV format

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00052: Background processing and caching for performance on large datasets

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00053: Handling of patrons with outstanding fines during inactivity check

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.

> We
> should probably handle those differently.

### C-00054: Support for Linux or Solaris server environment

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.

> OE-2: The system must operate on a Linux or Solaris server environment.
>       [* High Priority]

### C-00055: Support for web browser or Windows-compatible client access

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.

> OE-3: The system must be accessible through a web browser or a Windows-compatible
>       client.
>       [* High Priority]

### C-00056: Web browser compatibility with IE and Firefox

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.

> OE-4: If web-browser based, the system must be accessible through Microsoft
>       Internet Explorer (version 6.0 and later) and Mozilla Firefox (version
>       2.0 and later).
>       [* Medium Priority]

### C-00057: Support for accessibility features

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.

> OE-5: The system must be accessible with screen-reading software, screen-
>       magnification software, and other assistive technology programs designed
>       to increase accessibility.
>       [* High Priority]

### C-00058: Use of a fully relational database back-end

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.

> CO-1: The system must use a fully relational database back-end. [* High Priority]

### C-00059: Production of standards-compliant HTML output for web components

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.

> CO-2: The system must produce standards-compliant HTML output for web-based
>       components.
>       [* High Priority]

### C-00060: Security roles for user rights and privileges

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.

> CO-4: User rights and privileges will be controlled through security groups and
>       or "roles" that allow access control for individuals, workgroups, and
>       arbitrary staff groups.
>       [* High Priority]

### C-00061: Provision of complete data specifications for records

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.

> UD-1: The developer must provide complete data specifications for authority
>       records, bibliographic records, order records, item records, hold/request
>       records, and other records maintained or accessed by the Management
>       Processes.
>       [* High Priority]

### C-00062: High-level description of major processes for import/export and validation

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.

> UD-2: The developer must provide a thorough high-level description of major
>       processes, including bibliographic record import and export, validation
>       of bibliographic records against internal and external authority sources,
>       and standard reports.
>       [* Medium Priority]

### C-00063: Online help system in HTML with descriptions and illustrations

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.

> UD-3: The system must provide an online, hierarchical, and cross-linked help
>       system in HTML that describes and illustrates all system functions.
>       [* High Priority]

### C-00064: Error reporting and feedback mechanisms

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.

> UD-4: The system must provide thorough high-level error reporting and feedback,
>       and shall allow low-level query-specific feedback for Local and Global
>       System Administrators from the front-end interface.
>       [* Medium Priority]

### C-00065: Integration with vendor websites via APIs or standard-format data files

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.

> DE-2: Management Processes interface with a variety of vendor websites, via
>       published APIs and/or automated transfer of standard-format data files
>       (e.g., USMARC21, EDIFACT).

### C-00066: Interaction with patron interface (OPAC)

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.

> DE-3: Management Processes interact with a patron interface, also known as an
>       Online Public Access Catalog (OPAC).

### C-00067: Support for Fine-Grained Reports

Source: `early_draft_srs_galecia.txt`, chunk `CH-002`.

> able to support the fine-grained reports requirements as
> described in the attached specification (see Appendix B).

### C-00068: Ability to edit recurring reports

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.

> Ability to edit recurring reports by adding or removing report selections
>   as well as editing the email addresses

### C-00069: Output result customization with multiple columns and percentages

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.

> Ability to determine the output results in a way such that a result could have
>   one column for last month's circs, another for previous month's circ, a percent
>   difference column, previous year's month column, a percent difference from
>   last month to last year's month column

### C-00070: Batch conversion report system

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.

> The system provides a report to assist in the batch conversion of statuses

### C-00071: Ability to edit canned reports for display purposes

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.

> Ability to edit canned report for display purposes such as adding shelving
>   location as a display

### C-00072: Adding canned reports via permission level

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.

> Ability to add more canned reports via permission level

### C-00073: Retrieve list of deleted items for WorldCat update

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.

> Ability to get a list of items deleted that was the last copy owned by the
>   library system in order to update WorldCat

### C-00074: Prioritize reports in queue

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.

> Ability to prioritize certain types of reports so they will pop to the top of
>   the queue over resource-consuming reports

### C-00075: Total and usage count reporting on items

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.

> Ability to have a total use count on items as well as a use count broken down
>   by usage date range such as an FY use count or monthly use count

### C-00076: Retrieve total circulation including various transaction types

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.

> Ability to retrieve total circ including checkouts, renewals, and noncats
>   with a breakdown displaying those circ types

### C-00077: Upload filtering data from text files

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.

> Ability to upload a text file such as barcodes or TCN to use for filtering
>   on a report

### C-00078: Run reports for different notice types

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.

> Ability to run reports for pre-overdue, overdue, and holds notices sent

### C-00079: Pivot table output

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.

> Pivot table output

### C-00080: Proven output quality

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.

> Tested and proven output

### C-00081: Cancel scheduled or running reports

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.

> Ability to cancel a report that has already been scheduled to run or is
>   currently running

### C-00082: Include nulls and blanks in results

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.

> All nulls and blank fields must be included in the results no matter what is
>   being filtered or displayed

### C-00083: Real-time reporting capability

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.

> Ability to have real time reporting

### C-00084: Historical reporting with data warehouse

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.

> Ability to have historical reporting - a reporting warehouse such that data
>   can be acquired on a given date or date range

### C-00085: Clear definition of selection criteria and display of date range

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00086: Filtering by survey name without survey ID

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.

> Ability to select the survey name and not have to enter the survey id for
>   filtering

### C-00087: Report on deleted items that were last copies in the facility

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.

> Ability to run a report on deleted items that were the last copy in the facility

### C-00088: Pull MARC record fields for report display

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.

> Ability to pull MARC record fields so that they appear on a single row of data

### C-00089: Run reports on transactions within specific date/time and staff workstation

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.

> Ability to run a report on transactions that occurred on x date and time on x
>   workstation or by x staff

### C-00090: Valuation of Items Report Functionality

Source: `email_financial_reports.eml`, chunk `CH-001`.

> Value of items report - staff should be able to get the value of items
>    based on data in item records. This could be the entire collection, or a
>    portion. For example, they want to be able to get:
>    - Value of all items with status "longoverdue"
>    - Value of all DVDs in children's collection
>    - Value of entire collection

### C-00091: Query Tool Interface

Source: `email_report_features.eml`, chunk `CH-001`.

> We need a user-friendly interface for designing queries against
>    all record types. Staff should be able to select fields to query, select
>    values from picklists, use regular expressions from a dropdown, and use
>    Boolean operators.

### C-00092: Report Templates Creation and Management

Source: `email_report_features.eml`, chunk `CH-001`.

> Admins need to create report templates that are available
>    to staff. Templates should be runnable as-is or modified. Changes shouldn't
>    compromise results. Admins should be able to limit which filters and display
>    fields can be altered.

### C-00093: Report Cloning Functionality

Source: `email_report_features.eml`, chunk `CH-001`.

> The key benefit of templates is consistency. We want to make sure that when
> the director asks for "the weeding report," everyone runs the same report with
> the same criteria. Templates ensure this.

### C-00094: Permission Levels and Role-Based Access Control

Source: `email_report_features.eml`, chunk `CH-001`.

> The permissions need to be easy to administer. If I change someone from "Staff"
> to "Manager," their report permissions should update automatically based on
> the role.

### C-00095: Board and Activity Reports Specification

Source: `email_report_features.eml`, chunk `CH-001`.

> Pre-defined reports for library boards with basic statistics
>    (Georgia Annual Report requirements). Activity reports showing traffic and
>    volume of use - checkouts, check-ins, holds placed, holds filled.

### C-00096: Transaction Archive with Privacy Compliance

Source: `email_report_features.eml`, chunk `CH-001`.

> Transactions archived protecting patron privacy per
>    State Law, while providing useful demographic statistics.

### C-00097: Query Selections Display

Source: `email_report_features.eml`, chunk `CH-001`.

> System provides query selections along with results.

### C-00098: Report Queuing Visibility and Priority

Source: `email_report_features.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00099: Queue Prioritization Mechanism

Source: `email_report_features.eml`, chunk `CH-001`.

> A director's
> board report should be able to jump ahead of a staff member's ad-hoc query.

### C-00100: Support for Multiple Staff Login Methods

Source: `email_staff_login.eml`, chunk `CH-001`.

> The system should support
> BOTH methods - streamlined login (e.g. card swipe) AND traditional login
> (individual login and password). The streamlined method should be optional but
> available.

### C-00101: Individual Authentication Tracking

Source: `email_staff_login.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00102: Role-Based Access Control

Source: `email_staff_login.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00103: Access Control by Roles and Staff Groups

Source: `email_staff_login.eml`, chunk `CH-001`.

> Access control for individuals, workgroups, and arbitrary staff groups.

### C-00104: Administrative Ease for Roles and Permissions

Source: `email_staff_login.eml`, chunk `CH-001`.

> The system
> should make it easy to administer these roles - changing someone's permissions
> should be a simple matter of changing their role assignment

### C-00105: Missing Report Types for Circulation and Collection Analysis

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00106: Report Queue Visibility and Management

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00107: Advanced Scheduling and Delivery Options

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.

> No ability to select Run ASAP, Hourly, Daily, Weekly, Monthly, Yearly
> - No email delivery of reports
> - No address book for report delivery

### C-00108: Rich Output Formats and Customization

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00109: Historical and Real-time Reporting Infrastructure

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00110: Separate Reporting Environment and Migration Capabilities

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.

> No development/training environment separation
> - No configuration migration between environments

### C-00111: Compliance and Accessibility Features

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.

> No accessibility support for report interface
> - No online help system integrated with reports

### C-00112: Fine-Grained Permissions and Security Controls

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.

> Current permission model:
> - Staff can run any report they can access
> - No fine-grained control over who can create vs. run reports

### C-00113: Support for Open Template Reporting and Snapshot Reports

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00114: Uncataloged Material Inventory Tracking

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.

> The requirements are: quick distribution (we need to process these fast),
> minimal branch labor (we can't spend a lot of time per item), and ability to
> identify how the material is being used.

### C-00115: Branch Transfer Utility with Query and Reversion Features

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00116: Missing and Damaged Items Report

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.

> We do monthly shelf reading and mark items as missing. I need a report
> that shows all missing and damaged items per branch.

### C-00117: In-Transit Items Regional Report with Configurable Thresholds

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00118: Weeding and Purging Reports with Custom Criteria

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00119: Orphan Record Clean-up Operations

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.

> Right now,
> cleaning up these orphaned records takes forever.

### C-00120: Deletion Tracking and Audit Logs

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00121: Shelf Space and Collection Management Reports

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.

> The shelf space report is important for collection management. For each
>    genre and format, I need to compare:
>    - Percentage of total circulations
>    - Percentage of the collection
>    - Percentage of total shelf space

### C-00122: Material Volume Metrics Reports

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.

> The material volume report helps me understand how much we have. I need to
>    report on volume based on acquisitions, items on shelf, and items in
>    circulation, broken down by categories like total items, holds, adult
>    fiction, board books, etc.

### C-00123: Data Quality Reports for Records and Items

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.

> Data quality reports - items with invalid item type, items with long call
>    numbers, bibliographic records with no item records.

### C-00124: Last Edit Date Display on Reports

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.

> I need to be able to see the last edit date on reports, but it should be
>    only when the item is edited and not include the last circulation.

### C-00125: Server Environment Compatibility

Source: `interview_sysadmin_2009-05-10.txt`, chunk `CH-001`.

> Our main server is a Red Hat Enterprise Linux 5 box with dual quad-core
> processors and 32GB of RAM. It runs PostgreSQL 8.3 for the database. We also
> have a secondary site that runs Solaris 10 on SPARC hardware for disaster
> recovery and reporting.

### C-00126: Background Report Processing Support

Source: `interview_sysadmin_2009-05-10.txt`, chunk `CH-001`.

> Right now, when someone runs a complex
> report, it can tie up the database and slow down the circulation client. We
> need to make sure reports can be queued and processed in the background. Or we
> need read-only reporting replicas. The key requirement is that searches and
> reports can be processed during open hours without disrupting other system
> functions.

### C-00127: Browser Compatibility Requirements

Source: `interview_sysadmin_2009-05-10.txt`, chunk `CH-001`.

> Most of our libraries standardize on Microsoft
> Internet Explorer, but many have moved to Firefox. IE 6 is still common in
> our environment - I know it's old, but upgrading browsers on 200+ library
> computers is expensive and time-consuming. Firefox 2.0 is also still in use
> at some locations. So we need to support IE 6.0+ and Firefox 2.0+.

### C-00128: Accessibility Compliance

Source: `interview_sysadmin_2009-05-10.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00129: Database Architecture Compatibility

Source: `interview_sysadmin_2009-05-10.txt`, chunk `CH-001`.

> We're using PostgreSQL now, which is a fully relational database.
> That's good - it means we can write complex joins. The reporting system needs
> to work with the relational structure, not fight against it. Some systems try
> to use denormalized reporting schemas, but that creates sync issues. I'd
> prefer to keep everything in the main relational database.

### C-00130: User Permissions Management

Source: `interview_sysadmin_2009-05-10.txt`, chunk `CH-001`.

> PINES uses a role-based system. We have different levels of access:
>   - Patron (public access through OPAC)
>   - Staff (basic circulation functions)
>   - Local Admin (branch manager - can run reports, configure local settings)
>   - Global Admin (IT staff - full system access)
> 
> The permission system needs to be controlled through security groups and/or
> "roles." This allows access control for individuals, workgroups, and arbitrary
> staff groups. The system needs to make it easy to administer these roles.
> Changing someone's permissions should be a simple matter of changing their
> role assignment.

### C-00131: Development and Training Environments

Source: `interview_sysadmin_2009-05-10.txt`, chunk `CH-001`.

> We definitely need separate environments. Developers need a place to
> test new reports without affecting production. And new staff members need a
> training environment where they can practice running reports without worrying
> about making mistakes.
> 
> The key is that configurations developed in training/dev need to be migratable
> to production. We need export/import functionality for report templates,
> permission settings, and other configuration.

### C-00132: Operational Separation from OPAC

Source: `interview_sysadmin_2009-05-10.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00133: Help System Accessibility and Navigation

Source: `interview_sysadmin_2009-05-10.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00134: Reports Interface Software Requirements Specification Adaptation

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.

> Katherine explained that King County Library System (WA) had previously worked
> with Galecia Group to develop a comprehensive Software Requirements Specification
> for a reports interface. PINES staff decided to use that as a foundation and
> adapt it for our specific needs. She mentioned that Lori Ayre and Lucien Kress
> from Galecia Group had been contacted and were willing to share their draft.

### C-00135: Functional Requirements for Reports and Management Processes

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.

> Katherine explained
> that the group would focus on Management Processes - that is, reports and
> analysis tools used by library managers, administrators, and staff for
> planning, evaluation, and oversight purposes. She clarified that this does NOT
> include day-to-day patron-facing functions (those are part of the OPAC and
> circulation client).

### C-00136: Report Development and Testing Responsibilities

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.

> - Document optimal Reports functionality within a future Evergreen release
>      and develop a list of requirements.
>    - Become the Reports testing group, through which all new Reports development
>      would be filtered.

### C-00137: Report Templates Specification for PINES Libraries

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.

> - Compile a list of reports needed for an Executive Reports Interface.
>    - Determine and create templates needed for all PINES libraries.

### C-00138: User Interface Focus on Functional Requirements

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.

> Katherine
> noted that while UI would eventually need detailed specification, for now the
> focus should be on functional requirements. She mentioned that UI and data
> structures would require further specification using an iterative, prototype-
> oriented methodology.

### C-00139: Management Process Data Scope Definition

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.

> The following scope items were identified:
> 
>   - Analyzing the Library collection and its use by patrons
>   - Analyzing branch capacity and optimal distribution of the collection
>   - Analyzing demographics and interests of patrons
>   - Analyzing staff productivity and workflow
>   - Tracking and verifying financial transactions

### C-00140: Development Approach and Documentation Readability Goals

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.

> Katherine stated that this SRS would be intended both for library managers and
> staff who may contribute additional requirements, and for software project
> managers and developers who will implement the requirements. She emphasized
> the need to aim for a high level of readability for a non-technical audience
> while providing enough specificity for developers.

### C-00141: Action Items for Requirement Gathering and Review Schedule

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.

> - Each member will conduct at least one interview with staff at their library
>     system to gather report needs (due by April 15, 2009)
>   - Katherine will circulate the King County / Galecia Group draft for reference
>   - A follow-up meeting is scheduled for July 20, 2009 to review findings
>   - A technical subcommittee meeting will be held in late June to discuss
>     architectural constraints

### C-00142: Support for Large Library Consortium Operations

Source: `meeting_minutes/meeting_2009-07-20_minutes.txt`, chunk `CH-001`.

> Management Processes must support the needs of a large, multiple-system
>       library consortium. Specifically, the system must support a library
>       consortium with 286 locations, 17 million annual circulations,
>       purchasing and processing over 900,000 items per year. It is highly
>       desirable that searches and reports can be processed during open hours
>       without disrupting other system functions.

### C-00143: Operating System Compatibility

Source: `meeting_minutes/meeting_2009-07-20_minutes.txt`, chunk `CH-001`.

> Management Processes shall operate on a Linux or Solaris server.

### C-00144: Access Method Requirements

Source: `meeting_minutes/meeting_2009-07-20_minutes.txt`, chunk `CH-001`.

> Management Processes shall be accessible through a web-browser or a
>       Windows-compatible client.

### C-00145: Browser Compatibility

Source: `meeting_minutes/meeting_2009-07-20_minutes.txt`, chunk `CH-001`.

> If web-browser based, Management Processes shall be accessible through
>       Microsoft Internet Explorer (v.6.0 and later) and Mozilla Firefox
>       (v.2.0 and later).

### C-00146: Accessibility Compliance

Source: `meeting_minutes/meeting_2009-07-20_minutes.txt`, chunk `CH-001`.

> Management Processes shall be accessible with screen-reading software,
>       screen-magnification software, and other software programs designed to
>       increase accessibility.

### C-00147: Use of Relational Database Back-End

Source: `meeting_minutes/meeting_2009-07-20_minutes.txt`, chunk `CH-001`.

> Management Processes shall use a fully relational database back-end.

### C-00148: Standards-Compliant HTML Output

Source: `meeting_minutes/meeting_2009-07-20_minutes.txt`, chunk `CH-001`.

> Management Processes shall produce standards-compliant HTML.

### C-00149: Configuration Migration Support

Source: `meeting_minutes/meeting_2009-07-20_minutes.txt`, chunk `CH-001`.

> Management Processes shall provide a development and training environment
>       with the ability to migrate configurations to a production environment.

### C-00150: Role-Based Access Control

Source: `meeting_minutes/meeting_2009-07-20_minutes.txt`, chunk `CH-001`.

> User rights and privileges will be controlled through security groups
>       and/or "roles" that allow access control for individuals, workgroups,
>       and arbitrary staff groups.

### C-00151: Public-Facing Catalog Independence

Source: `meeting_minutes/meeting_2009-07-20_minutes.txt`, chunk `CH-001`.

> These requirements shall not constrain functionality or features of the
>       Online Public Access Catalog (OPAC) module.

### C-00152: Data Specification Documentation

Source: `meeting_minutes/meeting_2009-07-20_minutes.txt`, chunk `CH-001`.

> The software developer shall provide complete data specifications for
>       authority records, bibliographic records, order records, item records,
>       hold/request records, and other records maintained or accessed by
>       Management Processes.

### C-00153: Process Description Documentation

Source: `meeting_minutes/meeting_2009-07-20_minutes.txt`, chunk `CH-001`.

> The software developer shall provide a thorough high-level description
>       of major processes, including bibliographic record import and export,
>       validation of bibliographic records against internal and external
>       authority sources, and standard reports.

### C-00154: Integrated Help System in HTML

Source: `meeting_minutes/meeting_2009-07-20_minutes.txt`, chunk `CH-001`.

> The system shall provide an online, hierarchical, and cross-linked help
>       system in HTML that describes and illustrates all system functions.

### C-00155: Error Reporting and Feedback

Source: `meeting_minutes/meeting_2009-07-20_minutes.txt`, chunk `CH-001`.

> The system shall provide thorough high-level error reporting and feedback
>       and shall allow low-level query-specific feedback for Local and Global
>       System Administrators from the front-end interface.

### C-00156: Relational Database Constraint

Source: `meeting_tech_subcommittee_2009-06-30.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00157: Configurable Transaction History Duration

Source: `survey_results_2009.txt`, chunk `CH-001`.

> 1. Transaction history maintained for X days (configurable), with monthly and
>    annual aggregates retained indefinitely.

### C-00158: Grouping of Transactions by Various Dimensions

Source: `survey_results_2009.txt`, chunk `CH-001`.

> 2. Transactions can be grouped by hour, terminal, branch, and system.

### C-00159: Counting All Check-in Types Individually and Cumulatively

Source: `survey_results_2009.txt`, chunk `CH-001`.

> 3. All types of check-in counted individually and cumulatively: book-drop,
>    terminal, by user or self-service.

### C-00160: Counting All Check-out Types Individually and Cumulatively

Source: `survey_results_2009.txt`, chunk `CH-001`.

> 4. All types of check-out counted individually and cumulatively: staff checkout,
>    self checkout, staff renewal, self checkout renewal, online renewal, OPAC
>    renewal.

### C-00161: Holds Counted by Placement Method

Source: `survey_results_2009.txt`, chunk `CH-001`.

> 5. Holds counted with method of placement: at staff desk, public computer,
>    or remotely.

### C-00162: Detailed Transaction Reports Including Holds and Check-outs

Source: `survey_results_2009.txt`, chunk `CH-001`.

> 6. Transactions report can show holds placed, holds filled, and check-outs per
>    patron, per library, per group of libraries, per system, per county.

### C-00163: Demographic Data Reporting with Anonymization

Source: `survey_results_2009.txt`, chunk `CH-001`.

> 7. Demographic statistics include transactions by geographical regions and age
>    ranges. Data must be anonymized.

### C-00164: Patron Behavior and Material Usage Statistics for Prediction

Source: `survey_results_2009.txt`, chunk `CH-001`.

> 8. System produces statistics to understand/predict patron behavior and use
>    of materials.

### C-00165: Creation and Modification of Report Templates by Administrators

Source: `survey_results_2009.txt`, chunk `CH-001`.

> 9. Report templates can be created by administrators and run as-is or modified.

### C-00166: Fine-Grained Permissions for Report Creation and Management

Source: `survey_results_2009.txt`, chunk `CH-001`.

> 10. Fine-grained permissions limit who can create and clone reports.

### C-00167: Shared Folders for Report Access Control

Source: `survey_results_2009.txt`, chunk `CH-001`.

> 11. Shared folders to allow/disallow staff from running specific reports.

### C-00168: Visible Report Queue Status

Source: `survey_results_2009.txt`, chunk `CH-001`.

> 12. Ability to see where your report is in the queue.

### C-00169: Shelf-space estimation

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00170: Auto-Revert Policy Specification

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00171: Retention and transaction-history window

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00172: Query History Tracking per Item

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00173: Resource Consumption Monitoring

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00174: Health Monitoring Functionality

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00175: Communication of System Updates

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00176: Configurable User Preference Settings

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00177: Accessibility Compliance Update

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00178: Additional Report Types Needed

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00179: Operational Separation from OPAC

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00180: Help System Navigation and Accessibility

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00181: Reports Interface Specification Adaptation

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00182: Missing Report Types for Circulation and Collection Analysis

Source: `conversations/conv_pines019_020_missing_intransit.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00183: Advanced Scheduling and Delivery Options

Source: `conversations/conv_pines019_020_missing_intransit.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00184: Report Queue Visibility and Management

Source: `conversations/conv_pines019_020_missing_intransit.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00185: Rich Output Formats and Customization

Source: `conversations/conv_pines019_020_missing_intransit.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00186: Reporting and Audit Trails for Deletions

Source: `conversations/conv_pines022_deletions.eml`, chunk `CH-001`.

> The system should count and track record deletions (e.g., item records,
> patron records) per location and per system.

### C-00187: Enhanced Reporting Queue Management

Source: `conversations/conv_pines022_deletions.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00188: Compliance Confirmation for Accessibility Standards

Source: `conversations/conv_pines022_deletions.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00189: Improved Error Reporting and Feedback Features

Source: `conversations/conv_pines022_deletions.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00190: Detailed Logs for Deletion Actions

Source: `conversations/conv_pines022_deletions.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00191: Unaccounted Reporting Features

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00192: Missing Report Types for Circulation and Collection Analysis

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00193: Report Queue Visibility and Management

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00194: Advanced Scheduling and Delivery Options

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00195: Rich Output Formats and Customization

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00196: Historical and Real-time Reporting Infrastructure

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00197: Operational Separation from OPAC

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00198: Help System Accessibility and Navigation

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00199: Support for Open Template Reporting and Snapshot Reports

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00200: Query Handling of Nulls

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00201: Support for User Query Visibility

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.

> The system should provide the query selections along with the results, so users
> can see what criteria were used to generate the report.

### C-00202: Query Selections Display

Source: `early_draft_srs_galecia.txt`, chunk `CH-002`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00203: Queue Management and User Visibility

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00204: Clear Definition of Report Selection Criteria and Date Ranges

Source: `early_draft_srs_galecia.txt`, chunk `CH-003`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00205: Financial Reporting Requirements for Value of Items

Source: `email_financial_reports.eml`, chunk `CH-001`.

> System can generate a report of the value of items (based on data in item
>    record) in the entire collection or a portion. Examples: value of all items
>    with status of "longoverdue", value of all DVDs in children's collection,
>    value of entire collection.

### C-00206: Compliance with Financial Reporting Standards and Audit Requirements

Source: `email_financial_reports.eml`, chunk `CH-001`.

> All reports and data archiving must comply with standard accounting practice
>    and state, county, and municipal auditing requirements.

### C-00207: Ease of Update for Financial Information

Source: `email_financial_reports.eml`, chunk `CH-001`.

> Financial information can be updated easily. A staff user can easily query
>    patron accounts with balances greater than X dollars.

### C-00208: Audit Trail for Transactions

Source: `email_financial_reports.eml`, chunk `CH-001`.

> The system maintains a ledger of patron payments, including which charges
>    payments are applied to, to facilitate reconciliation.

### C-00209: Additional Report Types for Collection Analysis

Source: `email_report_features.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00210: Report Queue Visibility and Management

Source: `email_report_features.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00211: Operational Separation from OPAC

Source: `email_report_features.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00212: Help System Accessibility and Navigation

Source: `email_report_features.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00213: Support for Open Template Reporting and Snapshot Reports

Source: `email_report_features.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00214: Real-Time Reporting Capability

Source: `email_report_features.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00215: Detailed Transaction Reporting Including Holds and Check-Outs

Source: `email_report_features.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00216: Valuation Reports with Financial Implications

Source: `email_report_features.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00217: Support for Filtering and Grouping by Demographics

Source: `email_report_features.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00218: Background Report Processing Support

Source: `email_report_features.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00219: Query History Tracking

Source: `email_staff_login.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00220: Consolidated Item Status Reports

Source: `email_staff_login.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00221: Replication Health Monitoring Functions

Source: `email_staff_login.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00222: Data Ownership and Retention Policies Documentation

Source: `email_staff_login.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00223: Operational Separation from OPAC

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00224: Help System Accessibility and Navigation

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00225: Reports Interface Software Requirements Specification Adaptation

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00226: Functional Requirements for Reports and Management Processes

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00227: Report Development and Testing Responsibilities

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00228: Report Templates Specification for PINES Libraries

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00229: User Interface Focus on Functional Requirements

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00230: Management Process Data Scope Definition

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00231: Development Approach and Documentation Readability Goals

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00232: Action Items for Requirement Gathering and Review Schedule

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00233: History Tracking of Deleted Items

Source: `interview_sysadmin_2009-05-10.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00234: Electronic Activity Reporting for Patrons

Source: `interview_sysadmin_2009-05-10.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00235: Inactivity Threshold Customization

Source: `interview_sysadmin_2009-05-10.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00236: Authentication Options and Individual Auditability

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00237: Permissions and Role Restrictions for Transfer & Report Actions

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00238: Development / Training Environments and Configuration Migration

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00239: Electronic activity inclusion for inactivity reports

Source: `meeting_minutes/meeting_2009-07-20_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00240: Inclusion of current mailing addresses in report for outreach

Source: `meeting_minutes/meeting_2009-07-20_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00241: Data Quality Documentation Requirement

Source: `meeting_tech_subcommittee_2009-06-30.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00242: Logging of Transfer Activities

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00243: Support for Time-Based and Event-Based Auto Revert

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00244: Automatic Reversion after Transfer Period

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00245: Transfer Delay Alerts and Notifications

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00246: Transfer Activity Logging and Item Transfer History

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00247: Permissions and Role Restrictions for Transfer & Report Actions

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00248: Help System and Error Reporting

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00249: Report Queue Visibility and Management

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00250: Shelf-space estimation

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.

> The system should provide the ability to report on the volume of material
> in a given library at any point in time, based on:

### C-00251: Query History Tracking per Item

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00252: Resource Consumption Monitoring

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00253: Health Monitoring Functionality

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00254: Communication of System Updates

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00255: Configurable User Preference Settings

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00256: Accessibility Compliance Update

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00257: Additional Report Types Needed

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00258: Operational Separation from OPAC

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00259: Help System Accessibility and Navigation

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00260: Reports Interface Specification Adaptation

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00261: User Interface Focus on Functional Requirements

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00262: Management Process Data Scope Definition

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00263: Development Approach and Documentation Readability Goals

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00264: Action Items for Requirement Gathering and Review Schedule

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00265: History Tracking of Deleted Items

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00266: Electronic Activity Reporting for Patrons

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00267: Inactivity Threshold Customization

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00268: Data Quality Documentation Requirement

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00269: Transfer Activity Logging and Item Transfer History

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00270: Shelf-space estimation

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00271: Auto-Revert Policy Specification

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00272: Retention and transaction-history window

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00273: Electronic activity inclusion for inactivity reports

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00274: Inclusion of current mailing addresses in report for outreach

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00275: Shelf-space estimation algorithm

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.

> The tricky part is #3. Shelf space isn't directly tracked in the database.
> We'd need to estimate based on item dimensions or use item count as a proxy.

### C-00276: Auto-Revert policy specifics

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00277: Retention and transaction-history window

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00278: Query history tracking per item

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00279: Resource consumption monitoring

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00280: Health monitoring functionality

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00281: Communication of system updates

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00282: Configurable user preference settings

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00283: Accessibility compliance update

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00284: Additional report types needed

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00285: Operational separation from OPAC

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00286: Help system accessibility and navigation

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00287: Reports interface specification adaptation

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00288: Missing report types for circulation and collection analysis

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00289: Advanced scheduling and delivery options

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00290: Report queue visibility and management

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00291: Rich output formats and customization

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00292: Historical and real-time reporting infrastructure

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00293: Detailed transaction reporting including holds and check-outs

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00294: Valuation reports with financial implications

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00295: Support for filtering and grouping by demographics

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00296: Background report processing support

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00297: Query history tracking

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00298: Consolidated item status reports

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00299: Replication health monitoring functions

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00300: Data ownership and retention policies documentation

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00301: Shelf-space estimation

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00302: Auto-Revert Policy Specification

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00303: Retention and transaction-history window

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00304: Query History Tracking

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00305: Resource Consumption Monitoring

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00306: Health Monitoring Functionality

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00307: Communication of System Updates

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00308: Configurable User Preference Settings

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00309: Electronic Activity Reporting for Patrons

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00310: Inclusion of current mailing addresses in report for outreach

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00311: Shelf-space estimation

Source: `conversations/conv_pines019_020_missing_intransit.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00312: Auto-Revert Policy Specification

Source: `conversations/conv_pines019_020_missing_intransit.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00313: Retention and transaction-history window

Source: `conversations/conv_pines019_020_missing_intransit.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00314: Query History Tracking per Item

Source: `conversations/conv_pines019_020_missing_intransit.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00315: Health Monitoring Functionality

Source: `conversations/conv_pines019_020_missing_intransit.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00316: Communication of System Updates

Source: `conversations/conv_pines019_020_missing_intransit.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00317: Configurable User Preference Settings

Source: `conversations/conv_pines019_020_missing_intransit.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00318: Accessibility Compliance Update

Source: `conversations/conv_pines019_020_missing_intransit.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00319: Additional Report Types Needed

Source: `conversations/conv_pines019_020_missing_intransit.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00320: Operational Separation from OPAC

Source: `conversations/conv_pines019_020_missing_intransit.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00321: Help System Accessibility and Navigation

Source: `conversations/conv_pines019_020_missing_intransit.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00322: Reports Interface Specification Adaptation

Source: `conversations/conv_pines019_020_missing_intransit.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00323: User Interface Focus on Functional Requirements

Source: `conversations/conv_pines019_020_missing_intransit.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00324: Action Items for Requirement Gathering and Review Schedule

Source: `conversations/conv_pines019_020_missing_intransit.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00325: Duplicate Candidate Assignments

Source: `conversations/conv_pines021_item_purging.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00326: Shelf-Space Estimation Methodology

Source: `conversations/conv_pines022_deletions.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00327: Auto-Revert Policy Specificity

Source: `conversations/conv_pines022_deletions.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00328: Retention and Transaction History Window

Source: `conversations/conv_pines022_deletions.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00329: Queue Prioritization Policy and Rules

Source: `conversations/conv_pines022_deletions.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00330: Accessibility Compliance Review

Source: `conversations/conv_pines022_deletions.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00331: Additional Report Capabilities for Circulation

Source: `conversations/conv_pines022_deletions.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00332: Operational Separation from OPAC

Source: `conversations/conv_pines022_deletions.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00333: Help System Usability and Navigation Improvements

Source: `conversations/conv_pines022_deletions.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00334: Reporting System Adaptation Process

Source: `conversations/conv_pines022_deletions.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00335: Shelf Space Estimation Investigations

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00336: Auto-Revert and Scheduled Reversion Processing

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00337: Deletion Audit Logging and Deletion Report Interface

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00338: Query Builder and Report Designer UI

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00339: Report Scheduling, Queue Management, Prioritization and Cancellation

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00340: Reversion / Auto-Revert Handling Procedure

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00341: Comprehensive Audit Trail of Access and Modifications

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00342: System Update Communication Mechanisms

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00343: Real-time Reporting Capability

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00344: Test specification for output validation

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00345: Inclusion of nulls in data insights

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00346: Historical data retrieval mechanisms

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00347: Support for background job processing for reports

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00348: Reports interface requirements documentation adaptation

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00349: Support for open template reporting and snapshot reports

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00350: Shelf-space estimation

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00351: Auto-Revert Policy Specification

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00352: Retention and transaction-history window

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00353: Query History Tracking per Item

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00354: Health Monitoring Functionality

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00355: Communication of System Updates

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00356: Configurable User Preference Settings

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00357: Accessibility Compliance Update

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00358: Additional Report Types Needed

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00359: Resource Consumption Monitoring

Source: `early_draft_srs_galecia.txt`, chunk `CH-002`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00360: Operational Separation from OPAC

Source: `early_draft_srs_galecia.txt`, chunk `CH-002`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00361: Help System Accessibility and Navigation

Source: `early_draft_srs_galecia.txt`, chunk `CH-002`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00362: Reports Interface Specification Adaptation

Source: `early_draft_srs_galecia.txt`, chunk `CH-002`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00363: Functional Requirements for Reports and Management Processes

Source: `early_draft_srs_galecia.txt`, chunk `CH-002`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00364: Report Development and Testing Responsibilities

Source: `early_draft_srs_galecia.txt`, chunk `CH-002`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00365: Financial Reporting for Patron Accounts

Source: `email_financial_reports.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00366: Payments Tracking

Source: `email_financial_reports.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00367: Standardized Financial Reports for Compliance

Source: `email_financial_reports.eml`, chunk `CH-001`.

> All reports and data archiving must comply with standard accounting practice
>    and state, county, and municipal auditing requirements.

### C-00368: Audit Trail for Payments

Source: `email_financial_reports.eml`, chunk `CH-001`.

> The system maintains a ledger of patron payments, including which charges
>    payments are applied to, to facilitate reconciliation.

### C-00369: Shelf-Space Estimation Algorithm

Source: `email_staff_login.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00370: Auto-Revert Policy Specification

Source: `email_staff_login.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00371: Retention and Transaction-History Window

Source: `email_staff_login.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00372: Query History Tracking

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00373: Resource Consumption Monitoring

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00374: Health Monitoring Functionality

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00375: Communication of System Updates

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00376: Configurable User Preference Settings

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00377: Accessibility Compliance Update

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00378: Additional Report Types Needed

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00379: Missing Report Types for Circulation and Collection Analysis

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00380: Operational Separation from OPAC

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00381: Help System Accessibility and Navigation

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00382: Reports Interface Software Requirements Specification Adaptation

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00383: Query Handling of Nulls

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00384: Detailed Logs for Deletion Actions

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00385: Help System and Error Reporting

Source: `interview_sysadmin_2009-05-10.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00386: Development / Training Environments and Configuration Migration

Source: `interview_sysadmin_2009-05-10.txt`, chunk `CH-001`.

> We definitely need separate environments. Developers need a place to
> test new reports without affecting production.

### C-00387: Shelf-space estimation

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00388: Auto-Revert Policy Specification

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00389: Retention and transaction-history window

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00390: Query History Tracking per Item

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00391: Resource Consumption Monitoring

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00392: Health Monitoring Functionality

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00393: Communication of System Updates

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00394: Configurable User Preference Settings

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00395: Accessibility Compliance Update

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00396: Additional Report Types Needed

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00397: Operational Separation from OPAC

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00398: Help System Accessibility and Navigation

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00399: Reports Interface Specification Adaptation

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00400: Functional Requirements for Reports and Management Processes

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00401: Report Development and Testing Responsibilities

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00402: Report Templates Specification for PINES Libraries

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00403: User Interface Focus on Functional Requirements

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00404: Management Process Data Scope Definition

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00405: Development Approach and Documentation Readability Goals

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00406: Action Items for Requirement Gathering and Review Schedule

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00407: Shelf-space estimation

Source: `meeting_minutes/meeting_2009-07-20_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00408: Auto-Revert Policy Specification

Source: `meeting_minutes/meeting_2009-07-20_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00409: Retention and transaction-history window

Source: `meeting_minutes/meeting_2009-07-20_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00410: Query History Tracking per Item

Source: `meeting_minutes/meeting_2009-07-20_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00411: Shelf-space estimation

Source: `meeting_tech_subcommittee_2009-06-30.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00412: Auto-Revert Policy Specification

Source: `meeting_tech_subcommittee_2009-06-30.txt`, chunk `CH-001`.

> ."

### C-00413: Retention and transaction-history window

Source: `meeting_tech_subcommittee_2009-06-30.txt`, chunk `CH-001`.

> ."

### C-00414: Query History Tracking per Item

Source: `meeting_tech_subcommittee_2009-06-30.txt`, chunk `CH-001`.

> ."

### C-00415: Resource Consumption Monitoring

Source: `meeting_tech_subcommittee_2009-06-30.txt`, chunk `CH-001`.

> ."

### C-00416: Health Monitoring Functionality

Source: `meeting_tech_subcommittee_2009-06-30.txt`, chunk `CH-001`.

> ."

### C-00417: Communication of System Updates

Source: `meeting_tech_subcommittee_2009-06-30.txt`, chunk `CH-001`.

> ."

### C-00418: Configurable User Preference Settings

Source: `meeting_tech_subcommittee_2009-06-30.txt`, chunk `CH-001`.

> ."

### C-00419: Accessibility Compliance Update

Source: `meeting_tech_subcommittee_2009-06-30.txt`, chunk `CH-001`.

> ."

### C-00420: Additional Report Types Needed

Source: `meeting_tech_subcommittee_2009-06-30.txt`, chunk `CH-001`.

> ."

### C-00421: Shelf-space estimation

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00422: Auto-Revert Policy Specification

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00423: Retention and transaction-history window

Source: `survey_results_2009.txt`, chunk `CH-001`.

> Transaction history maintained for X days (configurable), with monthly and
>    annual aggregates retained indefinitely.

### C-00424: Query History Tracking per Item

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00425: Resource Consumption Monitoring

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00426: Health Monitoring Functionality

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00427: Communication of System Updates

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00428: Configurable User Preference Settings

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00429: Accessibility Compliance Update

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00430: Additional Report Types Needed

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00431: Operational Separation from OPAC

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00432: Help System Accessibility and Navigation

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00433: Reports Interface Specification Adaptation

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00434: Functional Requirements for Reports and Management Processes

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00435: Report Development and Testing Responsibilities

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00436: Report Templates Specification for PINES Libraries

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00437: User Interface Focus on Functional Requirements

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00438: Management Process Data Scope Definition

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00439: Development Approach and Documentation Readability Goals

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00440: Action Items for Requirement Gathering and Review Schedule

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00441: History Tracking of Deleted Items

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00442: Electronic Activity Reporting for Patrons

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00443: Inactivity Threshold Customization

Source: `survey_results_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00444: Auto-Revert Policy Specification

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.

> "

### C-00445: Query History Tracking per Item

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.

> "

### C-00446: Resource Consumption Monitoring

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.

> "

### C-00447: Health Monitoring Functionality

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.

> "

### C-00448: Communication of System Updates

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.

> "

### C-00449: Configurable User Preference Settings

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.

> "

### C-00450: Accessibility Compliance Update

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.

> "

### C-00451: Additional Report Types Needed

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.

> "

### C-00452: Operational Separation from OPAC

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.

> "

### C-00453: Help System Accessibility and Navigation

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.

> "

### C-00454: Reports Interface Specification Adaptation

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.

> "

### C-00455: Functional Requirements for Reports and Management Processes

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.

> "

### C-00456: Report Development and Testing Responsibilities

Source: `conversations/conv_pines014_material_volume.eml`, chunk `CH-001`.

> "

### C-00457: Retention and Transaction History Window

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00458: Accessibility Compliance Update

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00459: Additional Report Types Needed

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00460: Operational Separation from OPAC

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00461: Help System Accessibility and Navigation

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00462: Reports Interface Specification Adaptation

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00463: Functional Requirements for Reports and Management Processes

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00464: Report Development and Testing Responsibilities

Source: `conversations/conv_pines015_capacity_interface.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00465: Shelf Space Estimation Overview

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00466: Auto-Revert Policy Definition

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00467: Retention Period Specification

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00468: Query History Visibility Feature

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00469: Resource Consumption Log

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00470: Health Monitoring Requirement

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00471: Structured Communication for System Updates

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00472: User Preference Configuration

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00473: Confirmation of Accessibility Compliance

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00474: Document Additional Report Types

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00475: Operational Independence from OPAC

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00476: Help System Usability Improvements

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00477: Reports Interface Specification Adaptation Clarification

Source: `conversations/conv_pines016_shelf_space.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00478: Shelf-space estimation algorithm

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00479: Query History Tracking per Item

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00480: Accessibility Compliance Update

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00481: Additional Report Types Needed

Source: `conversations/conv_pines018_item_transfer.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00482: Shelf Space Estimation Methodology

Source: `conversations/conv_pines019_020_missing_intransit.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00483: Auto-Revert Policy Specificity

Source: `conversations/conv_pines019_020_missing_intransit.eml`, chunk `CH-001`.

> ."

### C-00484: Shelf-space estimation

Source: `conversations/conv_pines021_item_purging.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00485: Auto-Revert Policy Specification

Source: `conversations/conv_pines021_item_purging.eml`, chunk `CH-001`.

> "

### C-00486: Retention and transaction-history window

Source: `conversations/conv_pines021_item_purging.eml`, chunk `CH-001`.

> "

### C-00487: Query History Tracking per Item

Source: `conversations/conv_pines021_item_purging.eml`, chunk `CH-001`.

> "

### C-00488: Resource Consumption Monitoring

Source: `conversations/conv_pines021_item_purging.eml`, chunk `CH-001`.

> "

### C-00489: Health Monitoring Functionality

Source: `conversations/conv_pines021_item_purging.eml`, chunk `CH-001`.

> "

### C-00490: Communication of System Updates

Source: `conversations/conv_pines021_item_purging.eml`, chunk `CH-001`.

> "

### C-00491: Configurable User Preference Settings

Source: `conversations/conv_pines021_item_purging.eml`, chunk `CH-001`.

> "

### C-00492: Accessibility Compliance Update

Source: `conversations/conv_pines021_item_purging.eml`, chunk `CH-001`.

> "

### C-00493: Additional Report Types Needed

Source: `conversations/conv_pines021_item_purging.eml`, chunk `CH-001`.

> "

### C-00494: Operational Separation from OPAC

Source: `conversations/conv_pines021_item_purging.eml`, chunk `CH-001`.

> "

### C-00495: Help System Accessibility and Navigation

Source: `conversations/conv_pines021_item_purging.eml`, chunk `CH-001`.

> "

### C-00496: Reports Interface Specification Adaptation

Source: `conversations/conv_pines021_item_purging.eml`, chunk `CH-001`.

> "

### C-00497: Functional Requirements for Reports and Management Processes

Source: `conversations/conv_pines021_item_purging.eml`, chunk `CH-001`.

> "

### C-00498: Report Development and Testing Responsibilities

Source: `conversations/conv_pines021_item_purging.eml`, chunk `CH-001`.

> "

### C-00499: Auto-Revert Policy Specificity

Source: `conversations/conv_pines022_deletions.eml`, chunk `CH-001`.

> "

### C-00500: Shelf Space Estimation Algorithm

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00501: Auto-Revert Policy Specification

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.

> "

### C-00502: Retention and Transaction-History Window

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.

> "

### C-00503: Query History Tracking per Item

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.

> "

### C-00504: Resource Consumption Monitoring

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.

> "

### C-00505: Health Monitoring Functionality

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.

> "

### C-00506: Communication of System Updates

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.

> "

### C-00507: Configurable User Preference Settings

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.

> "

### C-00508: Accessibility Compliance Update

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.

> "

### C-00509: Additional Report Types Needed

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.

> "

### C-00510: Operational Separation from OPAC

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.

> "

### C-00511: Help System Accessibility and Navigation

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.

> "

### C-00512: Reports Interface Specification Adaptation

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.

> "

### C-00513: Functional Requirements for Reports and Management Processes

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.

> "

### C-00514: Report Development and Testing Responsibilities

Source: `conversations/conv_pines023_patron_characteristics.eml`, chunk `CH-001`.

> "

### C-00515: Shelf-Space Estimation Investigations

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00516: Auto-Revert Policy Specification

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00517: Retention and transaction-history window

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00518: Query History Tracking per Item

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.

> ."

### C-00519: Resource Consumption Monitoring

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.

> ."

### C-00520: Health Monitoring Functionality

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.

> ."

### C-00521: Communication of System Updates

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.

> ."

### C-00522: Configurable User Preference Settings

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.

> ."

### C-00523: Accessibility Compliance Update

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.

> ."

### C-00524: Additional Report Types Needed

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.

> ."

### C-00525: Operational Separation from OPAC

Source: `conversations/conv_pines024_inactive_patrons.eml`, chunk `CH-001`.

> ."

### C-00526: Shelf-space estimation methodology

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00527: Auto-Revert policy specifics

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00528: Query History Tracking

Source: `early_draft_srs_galecia.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00529: Missing Report Types for Circulation and Collection Analysis

Source: `early_draft_srs_galecia.txt`, chunk `CH-002`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00530: Operations Process Documentation Requirement

Source: `early_draft_srs_galecia.txt`, chunk `CH-002`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00531: Shelf-space estimation

Source: `email_financial_reports.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00532: Auto-Revert Policy Specification

Source: `email_financial_reports.eml`, chunk `CH-001`.

> "

### C-00533: Retention and transaction-history window

Source: `email_financial_reports.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00534: Query History Tracking per Item

Source: `email_financial_reports.eml`, chunk `CH-001`.

> "

### C-00535: Resource Consumption Monitoring

Source: `email_financial_reports.eml`, chunk `CH-001`.

> "

### C-00536: Health Monitoring Functionality

Source: `email_financial_reports.eml`, chunk `CH-001`.

> "

### C-00537: Communication of System Updates

Source: `email_financial_reports.eml`, chunk `CH-001`.

> "

### C-00538: Configurable User Preference Settings

Source: `email_financial_reports.eml`, chunk `CH-001`.

> "

### C-00539: Accessibility Compliance Update

Source: `email_financial_reports.eml`, chunk `CH-001`.

> "

### C-00540: Additional Report Types Needed

Source: `email_financial_reports.eml`, chunk `CH-001`.

> "

### C-00541: Operational Separation from OPAC

Source: `email_financial_reports.eml`, chunk `CH-001`.

> "

### C-00542: Help System Accessibility and Navigation

Source: `email_financial_reports.eml`, chunk `CH-001`.

> "

### C-00543: Reports Interface Specification Adaptation

Source: `email_financial_reports.eml`, chunk `CH-001`.

> "

### C-00544: Functional Requirements for Reports and Management Processes

Source: `email_financial_reports.eml`, chunk `CH-001`.

> "

### C-00545: Report Development and Testing Responsibilities

Source: `email_financial_reports.eml`, chunk `CH-001`.

> "

### C-00546: Shelf-Space Estimation Algorithm

Source: `email_report_features.eml`, chunk `CH-001`.

> "

### C-00547: Auto-Revert Policy Specification

Source: `email_report_features.eml`, chunk `CH-001`.

> "

### C-00548: Retention and Transaction History Window

Source: `email_report_features.eml`, chunk `CH-001`.

> "

### C-00549: Query History Tracking per Item

Source: `email_report_features.eml`, chunk `CH-001`.

> "

### C-00550: Resource Consumption Monitoring

Source: `email_report_features.eml`, chunk `CH-001`.

> "

### C-00551: Health Monitoring Functionality

Source: `email_report_features.eml`, chunk `CH-001`.

> "

### C-00552: Communication of System Updates

Source: `email_report_features.eml`, chunk `CH-001`.

> "

### C-00553: Configurable User Preference Settings

Source: `email_report_features.eml`, chunk `CH-001`.

> "

### C-00554: Accessibility Compliance Update

Source: `email_report_features.eml`, chunk `CH-001`.

> "

### C-00555: Additional Report Types Needed

Source: `email_report_features.eml`, chunk `CH-001`.

> "

### C-00556: Operational Separation from OPAC

Source: `email_report_features.eml`, chunk `CH-001`.

> "

### C-00557: Help System Accessibility and Navigation

Source: `email_report_features.eml`, chunk `CH-001`.

> "

### C-00558: Reports Interface Specification Adaptation

Source: `email_report_features.eml`, chunk `CH-001`.

> "

### C-00559: Functional Requirements for Reports and Management Processes

Source: `email_report_features.eml`, chunk `CH-001`.

> "

### C-00560: Report Development and Testing Responsibilities

Source: `email_report_features.eml`, chunk `CH-001`.

> "

### C-00561: Missing Report Types for Circulation and Collection Analysis

Source: `email_staff_login.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00562: Operational Separation from OPAC

Source: `email_staff_login.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00563: Help System Usability and Navigation Improvements

Source: `email_staff_login.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00564: Query Handling of Nulls

Source: `email_staff_login.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00565: Reporting System Adaptation Process

Source: `email_staff_login.eml`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00566: Shelf-space estimation

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00567: Auto-Revert policy specifics

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00568: Retention and transaction-history window

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00569: Query history tracking per item

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00570: Operational separation from OPAC

Source: `evergreen_reference_2009.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00571: Shelf-space estimation algorithm

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00572: Auto-Revert Policy Specification

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.

> "

### C-00573: Retention and transaction-history window

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.

> "

### C-00574: Query History Tracking per Item

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.

> "

### C-00575: Resource Consumption Monitoring

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.

> "

### C-00576: Health Monitoring Functionality

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.

> "

### C-00577: Communication of System Updates

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.

> "

### C-00578: Configurable User Preference Settings

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.

> "

### C-00579: Accessibility Compliance Update

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.

> "

### C-00580: Additional Report Types Needed

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.

> "

### C-00581: Operational Separation from OPAC

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.

> "

### C-00582: Help System Accessibility and Navigation

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.

> "

### C-00583: Reports Interface Specification Adaptation

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.

> "

### C-00584: Functional Requirements for Reports and Management Processes

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.

> "

### C-00585: Report Development and Testing Responsibilities

Source: `interview_cataloging_2009-05-08.txt`, chunk `CH-001`.

> "

### C-00586: Missing Report Types Needed

Source: `interview_sysadmin_2009-05-10.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00587: Shelf-space estimation methodology

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00588: Auto-Revert policy specifics

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00589: Query history tracking per item

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.

> ."

### C-00590: Resource consumption monitoring

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.

> ."

### C-00591: Health monitoring functionality

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.

> ."

### C-00592: Communication of system updates

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.

> ."

### C-00593: Configurable user preference settings

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.

> ."

### C-00594: Accessibility compliance update

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.

> ."

### C-00595: Additional report types needed

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.

> ."

### C-00596: Operational separation from OPAC

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.

> ."

### C-00597: Help system accessibility and navigation

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.

> ."

### C-00598: Reports interface specification adaptation

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.

> ."

### C-00599: Functional requirements for reports and management processes

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.

> ."

### C-00600: Report development and testing responsibilities

Source: `meeting_minutes/meeting_2009-03-15_minutes.txt`, chunk `CH-001`.

> ."

### C-00601: Auto-Revert Policy Specification

Source: `meeting_tech_subcommittee_2009-06-30.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

### C-00602: Retention and transaction-history window

Source: `meeting_tech_subcommittee_2009-06-30.txt`, chunk `CH-001`.


**Unverified quote:** No exact quotation could be recovered. The source filename and chunk identify the text processed; they do not verify the model's interpretation.

