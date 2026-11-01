# RentYourExpert — architecture discussion

## Purpose and sources

- Week 05, Task 1: understand and compare three architectures, including implementation difficulties, before selecting one.
- Requirements: `Week_05_Designing/Tasks/data/RentYourExpert.txt` (system description and 35 user stories).
- Assignment: `Week_05_Designing/Tasks/Task_1.md`.
- These notes summarize proposals, user questions, explanations, trade-offs, assumptions, and conclusions. Update them as the conversation continues; proposed rules are not confirmed requirements.

## Stated requirements

- Three roles: customer, worker, administrator.
- Customers and workers can register, log in, view their own profile, and edit their information. Customers explicitly have logout; administrators can log in.
- Customers can browse the worker catalogue, search by skill and location, inspect worker pages, and read worker reviews.
- Customers can send requests to workers, list their own requests, and delete their requests. Workers can list requests addressed to them and accept or reject them.
- Customers can post questions to a worker and see questions from other customers. Workers can answer questions addressed to them.
- Customers can leave reviews and update or delete their own reviews.
- Administrators can list, inspect, create, and delete customers and workers; inspect all requests and add or delete requests; delete reviews; and delete a question together with its answers.
- The description calls for easy navigation, secure authentication and authorization, and worker management of profiles, projects, and communication. Detailed project-management behavior is not specified.

## Ambiguities and missing constraints

- Requests: required fields, dates, availability, acceptance rules, completion state, cancellation, and meaning of deletion are unspecified. Concurrent acceptance and deletion need a defined outcome.
- Reviews: the wording refers to received performance, but there is no explicit rule requiring a completed request, no completion workflow, and no rule about one review per request or worker.
- Accounts and permissions: whether one account can hold both customer and worker roles; whether anonymous browsing is allowed; worker verification; administrator provisioning; exact profile visibility.
- Search: whether location means city/region matching or distance; skill matching; meaning of an available worker.
- Q&A: visibility boundaries, answer multiplicity, editing rights, notifications, and moderation beyond administrator deletion.
- Deletion: whether to erase or retain account/request history and what happens to associated reviews, questions, answers, and requests.
- Projects: mentioned in the overview but not described in the user stories.
- Payments, checkout, pricing, schedules, private chat, and real-time delivery are not explicitly required. The administrator story uses the word e-commerce, which does not by itself define a payment workflow.
- No measurable targets for traffic, response time, uptime, security controls, retention, budget, team size, deployment environment, or integrations.

## Provisional assumptions for discussion (not requirements)

- Start with a browser-based application and a small development team; revisit if the user supplies different constraints.
- Treat requests as service enquiries, without payment or scheduling implementation unless clarified.
- Require sign-in for state-changing actions and enforce role and ownership checks on the server.
- Use ordinary page-based Q&A initially; live chat and immediate notifications are optional additions.
- No architecture choice has been made. Scale and operational constraints remain unconfirmed.

## Three proposed approaches

1. **Layered modular monolith:** one deployed application with internal modules for accounts, catalogue, requests, Q&A, reviews, and administration, generally sharing a relational database. Worth considering for straightforward transactions, local development, and a small team; requires discipline to preserve module boundaries.
2. **Microservices:** independently deployed domain services with service-owned data, communicating through APIs and possibly events. Worth considering for independent scaling and team ownership; adds distributed failure handling, consistency, and operational costs.
3. **Managed serverless backend:** web client plus managed authentication/database, short-lived functions for trusted workflows, and database access policies. Worth considering for a small team seeking lower server-operation effort and intermittent demand; introduces provider coupling, policy complexity, and platform constraints. Serverless describes execution/operations rather than necessarily a different domain decomposition; this proposal specifically moves selected access directly to managed services and privileged work into functions.

## Discussion plan and status

- Begin with requirements and resolve the most consequential uncertainties.
- Discuss approach 1 first, then leave room for follow-up before approach 2 and approach 3.
- For each: components and communication; end-to-end actions; storage/authentication/authorization; system-specific trade-offs; low-level failures and consistency; development/testing/deployment/maintenance effort.
- Compare all three and recommend only after discussion, stating the assumptions behind the choice.
- User clarified that they are not the customer and cannot resolve requirement ambiguities. Proceed using the supplied requirements and explicitly provisional implementation decisions. Do not ask the user to invent customer requirements.
- Continue one architecture at a time. Final comparison remains pending.

## Architecture 1: layered modular monolith

### Proposal and components

- One deployed application, internally divided into Accounts/Profiles, Catalogue/Search, Requests, Q&A, Reviews, and an administrative interface using the same business operations with explicit administrator privileges.
- Browser sends HTTPS requests to application endpoints. Presentation/controllers handle HTTP input and output; application/domain services enforce business rules; data access reads/writes a shared relational database. Module calls are ordinary in-process calls.
- A module is a boundary in code, not a separate running service. A layer separates technical responsibilities. Neither requires microservices.
- Suggested storage: relational tables for accounts, roles, worker profiles, skills, worker-skill links, requests, questions, answers, and reviews. Foreign keys keep references valid; indexes support worker/location/skill search and request lists. Pagination limits result sizes.
- Authentication can use a mature framework's password hashing and server-side sessions with secure cookies. Authorization checks role AND ownership/recipient on every server operation; the browser is not trusted to enforce permissions. CSRF protection is needed for cookie-authenticated changes. Administrator assignment must be privileged, never a public registration field.

### Concrete end-to-end workflows

- Search/profile: browser submits skill/location filters; catalogue module validates filters and queries indexed worker data; returns a page of workers; profile page fetches public worker details, reviews, and Q&A, excluding private account information.
- Create request: browser submits worker and request content; server authenticates customer, validates input and active worker, creates a pending request in a transaction, then returns its ID. Customer and worker lists filter by authenticated identity.
- Accept/reject: server verifies the caller is the addressed worker; conditionally updates a pending request. A conflicting update returns a conflict response instead of silently overwriting another action.
- Q&A: authenticate customer and validate target worker before inserting question; an answer requires the addressed worker's identity. Administrator deletion removes question and answers together in a database transaction, potentially using an explicit cascade.
- Reviews: customer can create and edit/delete their own review; administrator can delete any review. Do not invent a completed-work eligibility check without a defined completion workflow. Worker pages read the saved reviews.
- Profiles/accounts: self-service edits allow only approved profile fields; administrator actions have separate privilege checks. Account deletion policy remains unresolved because related content may need retention or removal.

### Low-level implementation and failure cases

- A transaction groups database changes so all commit or none do. It cannot define missing business policy and does not automatically solve every race.
- Illustrative assumption: both customer deletion and worker acceptance require a pending request. Conditional state/version checks let one win and return a conflict to the other. This is an example policy, not a confirmed requirement; accepted-request deletion remains unspecified.
- A lost response after successful creation can cause a retry to create a duplicate request. Use a client operation/idempotency key with a database uniqueness constraint and return the prior result for the same operation; distinguish retries from intentionally new requests.
- Check worker active status and coordinate account deletion with request creation inside transactions using suitable locks/constraints. A prior standalone existence check can race with deletion.
- Do not apply universal cascading deletion to accounts: define the related-record policy first. Question/answer deletion is explicitly required and can be atomic.
- Database failure: return an error without reporting success. If a response is lost after commit, operation keys resolve retry uncertainty. External notification failure must not undo a successful request; if added later, store a notification job alongside the request and retry delivery separately.
- One database simplifies atomic updates, but large unindexed queries, lock contention, and excessive per-row queries can still harm performance.

### Benefits and trade-offs

- Fits closely related data and administrative workflows, reduces network failure points, and gives a small team one repository/deployment to debug.
- Modules can still have unit and integration tests and clear ownership. Shared deployment and database can become coupling points; preserve module interfaces and avoid arbitrary cross-module writes.
- Multiple application instances behind a load balancer can scale a monolith; sessions must be shared or otherwise work across instances. Database capacity remains a shared constraint.
- A bad release can affect all features. Independent per-feature deployment/scaling is limited. Operational simplicity does not remove security, backup, or availability work.

### Development, testing, deployment, maintenance

- Relatively low initial infrastructure effort: application, relational database, HTTPS hosting, migrations, logs, and backups.
- Test authorization failures (e.g. editing someone else's review, accepting another worker's request), transaction behavior, concurrent state changes, deletion, and key browser workflows. Use the real database engine for important integration tests.
- Deploy a versioned application and compatible database migrations; verify health, monitor errors/latency, and test backup restoration. Application rollback does not automatically reverse destructive schema migrations.
- Maintain framework/security updates, database indexes, module boundaries, and regression tests. Later extraction into services is possible but incurs real data and interface migration work.

### Understanding check and status

- Question: what must the server check if a signed-in customer changes a review ID in an edit request to another customer's review? Expected explanation: authentication alone is insufficient; authorization must verify ownership (or explicitly permitted administrator action).
- Architecture 1 presented; follow-up discussion pending. Architectures 2 and 3 and final recommendation remain pending.

### Follow-up: concrete technology choices

- User asked: which framework, database engine, and hosting environment would be used?
- Proposed concrete stack for architecture 1: Python/Django, server-rendered Django templates with HTML/CSS and small amounts of JavaScript, PostgreSQL, and a Linux web service on Render with managed Render PostgreSQL. This is a discussion proposal, not an implementation or hosting purchase, and not a choice of architecture over the other two.
- Django apps represent domain modules within one deployment. Its ORM maps Python models to relational tables, while migrations track schema changes. Explicit service functions hold shared business rules used by customer/worker views and administrator operations.
- Django provides accounts, password hashing, groups/permissions, and cookie sessions. Ownership/recipient authorization still requires our code; login throttling also requires additional configuration/tooling.
- Customize Django admin for internal customer/worker/request/review/Q&A management; ensure its operations use business rules rather than bypassing them. Customer and worker pages use custom templates.
- PostgreSQL supports relational links, indexes, and transactions useful for requests and atomic question/answer deletion. Start with skill/city filters; geographic distance search remains unspecified.
- Proposed production flow: browser -> Render HTTPS endpoint -> Linux Gunicorn/Django process -> managed PostgreSQL. Use WhiteNoise for static CSS/JS. Keep credentials in environment configuration and apply versioned migrations during releases. Managed hosting reduces infrastructure work but application security, plan selection, backups/restoration, and migration safety remain our responsibilities; no free-tier or availability guarantees assumed.
- Develop with Python virtual environment and PostgreSQL locally (Docker optional); run database-sensitive tests against PostgreSQL too.
- Trade-offs: productive integrated framework and simpler frontend/deployment; less suitable if a highly interactive frontend or independently deployed clients become requirements. Python/Django familiarity is an unconfirmed team assumption. The architecture also permits other frameworks.
- Official documentation consulted: https://docs.djangoproject.com/en/5.2/topics/auth/ ; https://docs.djangoproject.com/en/5.2/ref/contrib/admin/ ; https://www.postgresql.org/docs/current/tutorial-transactions.html ; https://render.com/docs/deploy-django . Exact dependency versions would be selected and pinned during implementation, not inferred from old tutorial examples.

## Architecture 2: microservices

### Transition and assumptions

- User requested proceeding to the second architecture after the monolith technology follow-up. No answers to understanding checks or final architecture choice have been given.
- Keep the same functional scope. Service boundaries, event messaging, and token-based identity below are design proposals, not additional customer requirements.

### Components, responsibilities, and technology

- Browser UI calls an API gateway: a common entry point that routes requests. The administrator UI also uses authorized service APIs, never direct cross-service database writes.
- Identity/accounts service owns credentials, role assignments, and account status. Worker catalogue service owns public worker profiles, skills, and search data. Requests service owns request states. Community service owns questions, answers, and reviews; keeping questions/answers together permits atomic deletion.
- Each service owns its data and schema. PostgreSQL can be used per service, initially as separately permissioned databases on one database server; sharing hardware still shares failure/capacity risks. Services must not query each other's tables directly.
- A concrete continuation of the previous stack is Python/Django per service and PostgreSQL, with separate Linux application deployments. A separately deployed web UI calls the gateway; frontend technology need not change. An event broker provides durable asynchronous messages if events are used. Exact gateway/broker products are not selected at this discussion stage.
- Synchronous HTTPS APIs return an answer while a caller waits; asynchronous events report committed facts for consumers to process later. More services do not require a different programming language per service.

### End-to-end actions

- Login: identity service authenticates and issues a short-lived signed access token. Gateway and services validate trusted issuer, signature, intended audience, and expiry. Services enforce role and record ownership; ordinary clients cannot supply a trusted role header. Service-to-service calls also require authenticated identities and scoped permissions.
- Search/profile: catalogue service answers skill/location search from its own indexed data. Worker profile details and community reviews/Q&A can be fetched through separate calls or gateway aggregation. If community is unavailable, show a clearly unavailable reviews section rather than pretending there are zero reviews.
- Request creation: requests service validates customer permissions and worker availability/account status through an appropriate service API, then commits the request in its own transaction. A timeout in validation must not be interpreted as approval or as proof that the worker does not exist. A successful validation can still race with later account deletion.
- Accept/reject and customer deletion: requests service checks actor/recipient and performs conditional state changes in its own database; the concurrency problem remains local to this service. Retry-safe submission keys still matter.
- Q&A/reviews: community service handles question creation, worker answering, and review ownership. An administrator deleting a question and its answers uses one local transaction. Completed-work review eligibility is not invented; if later required, it introduces a dependency on request/completion information.
- Admin user/worker creation coordinates identity and profile creation. If the second step fails, retain a clearly incomplete provisioning state and retry or compensate; do not claim a complete account/profile pair exists.

### Distributed failures and consistency

- There is no ordinary single database transaction spanning independently owned service databases. One service may commit while another is offline.
- Illustrative deletion workflow: mark an account as deactivating, prevent new actions, publish a lifecycle event, let requests/catalogue/community apply the defined deletion or retention policy, and track completion. This multi-step process is a saga: local transactions with retries or compensating actions, rather than a global rollback. The retention policy remains unspecified.
- Existing tokens and cached worker state may remain temporarily valid. Short token lifetimes limit staleness but do not provide immediate revocation; sensitive operations may need an online status check and must define failure behavior. A normal remote check cannot guarantee atomicity with a subsequent write elsewhere.
- Transactional outbox: save a business update and an outgoing-event record in the same local transaction; a background publisher retries delivery. This avoids a committed deletion/request with a permanently lost event after a crash.
- Expect duplicate event deliveries: consumers deduplicate by event ID, and state/version checks prevent old events from overwriting newer state. Broker acknowledgement after processing, durable publication, and retry monitoring are required.
- Eventual consistency means services can temporarily show different information while events propagate. It is acceptable only where the business workflow permits delay; security-sensitive actions need stronger coordination, not a blanket assumption that stale data is harmless.
- Use bounded timeouts and limited retries for safe/idempotent operations; show pending/unknown outcomes appropriately. Correlation IDs link logs across calls. Monitor failures and queues and provide recovery for repeatedly failing messages.

### Benefits, limitations, and effort

- Benefits: independent releases, targeted scaling of catalogue/community traffic, service/data ownership for separate teams, and some failure isolation (e.g. review outage need not stop searching). Synchronous dependencies can still propagate failures.
- Costs for this system: several network hops and deployments for tightly related profiles/requests/reviews, harder administrator workflows, duplicated identity/status information, and greater operating cost. No stated scale or team requirements currently justify these costs.
- Development requires API/event contracts and a local environment with services, databases, and messaging. Unit/service integration tests are supplemented by contract tests, end-to-end workflows, and failure tests for duplicate/out-of-order events and partial provisioning/deletion.
- Deployment requires independent pipelines and backward-compatible API/event/schema evolution because old and new service versions coexist. Maintenance adds centralized logs, tracing, service credentials, queue monitoring, backups, and cross-service restore/reconciliation procedures. Restoring each database separately can produce contradictory states.
- Architecture 2 presented. Architecture 3 and final comparison/recommendation remain pending.

## Architecture 3: managed serverless backend

### Transition, distinction, and proposed stack

- User requested the third architecture. No final selection or answers to understanding checks have been supplied.
- Proposed stack: React/TypeScript browser UI served as static assets by a CDN/static host; Supabase Auth; managed PostgreSQL and generated data API; PostgreSQL functions for atomic workflows; Supabase Edge Functions (TypeScript/Deno) for privileged identity administration or external integrations.
- Serverless means provider-managed execution and scaling, not the absence of servers. This proposal differs structurally from the monolith: selected client operations go directly to a managed data API guarded by database policies; logic resides in policies, database functions, and selected hosted functions rather than one application server. Serverless and microservices are not mutually exclusive labels; this is a particular backend-as-a-service design with one shared relational database, not function-per-entity microservices.
- Provider hosts database/auth/functions; static host serves UI. Database remains a provisioned managed resource and is not assumed to scale without limits or cost. No exact hosting plan, free-tier guarantee, or dependency versions selected.

### Components and communication

- Browser authenticates through Supabase Auth and includes its access token on managed API/function calls.
- Data API handles permitted reads and simple writes. Row-level security (RLS) policies enforce which rows a caller may read/change. Table/column grants and carefully designed functions separately limit which fields and transitions can change.
- PostgreSQL stores profiles, protected roles/account status, skills, requests, questions, answers, and reviews. Expose only intended public profile fields; RLS filters rows, not private columns inside those rows.
- Database functions implement workflows such as create_request, accept_request, and delete_question atomically. Restrict execution privileges, default to caller privileges, and carefully audit any elevated SECURITY DEFINER function, including caller checks and a fixed safe search_path.
- Edge Functions handle trusted operations needing secrets or administrative Auth APIs. Verify caller identity and administrator role before using privileged credentials; service-role credentials bypass RLS and must never appear in the browser.

### End-to-end workflows and permissions

- Registration/login: managed Auth establishes identity; create the app profile reliably via a minimal database trigger or retry-safe provisioning workflow. Customer/worker registration choice must be validated; no public admin assignment. Prevent access with incomplete profile provisioning. Roles must be in protected storage, not user-editable metadata.
- Search: browser calls data API for paginated skill/location queries against allowed public profile data. Profile views read permitted reviews and Q&A. Whether guests may browse remains unspecified; policies can initially require login without declaring it a customer requirement.
- Request creation: browser calls a database function that validates the authenticated customer, worker active state, and submitted fields, then inserts pending request with a retry-safe operation key. Lists use customer/recipient row policies.
- Accept/reject/delete request: functions perform role/recipient/ownership checks and conditional state updates in the database. Prevent direct table updates from bypassing these functions or changing worker_id, customer_id, or arbitrary status fields. Concurrent acceptance/deletion uses the same explicit example policy as architecture 1, not a newly confirmed rule.
- Q&A: customers insert questions for valid workers; only the addressed worker may answer. Reviews can be created/edited/deleted by their author; admin moderation uses protected paths. Do not add unsupported completed-work eligibility requirements.
- Administrator question deletion runs one database transaction including answers. Administrator account creation/deletion may involve Auth APIs and application records across separate calls: track intermediate states and retry/reconcile failures; define data retention policy before implementing account removal.

### Consistency and failure cases

- One PostgreSQL database retains local transactions, unlike the microservices proposal. Several successive browser calls or Edge Function API calls are not automatically a single transaction: keep related database mutations inside one database function/transaction.
- RLS needs separate read/insert/update/delete coverage. Update checks must protect both the selected row and resulting ownership; row ownership alone does not restrict all columns. Test attempts to forge author IDs, change request recipients, elevate roles, and read private profile fields through raw APIs.
- Conditional updates/locks handle competing request actions. Unique operation keys handle timeout-after-commit retries; the UI must not assume a failed network response means nothing was saved.
- Function instances cannot rely on in-memory state surviving or being shared. Platform execution limits/cold starts and database connection limits affect design; keep request functions short and use durable queues for long-running optional work.
- Auth/database/platform outages affect dependent features; display errors and avoid claiming success until persistence is confirmed. Existing tokens may remain valid after account status changes, so sensitive database operations should consult protected active-status data where needed.
- External messages, if later added, use durable jobs/outbox and retries; do not assume a fire-and-forget function survives termination.

### Benefits, trade-offs, and effort

- Benefits: less server administration, managed identity, quick CRUD development, and relational transactions. Particularly plausible for a small team familiar with TypeScript/SQL and managed platforms.
- Costs: business/security rules are spread across UI, RLS, SQL functions, and Edge Functions; unsafe policies can expose direct API access; vendor coupling in authentication/API/function conventions; provider limits and usage-dependent costs; database remains a scaling constraint. PostgreSQL improves data portability without eliminating migration work.
- Development requires a frontend plus versioned schema/policy/function migrations. Tests must exercise the actual API as anonymous/customer/other-customer/worker/admin identities; privileged-key tests alone bypass the most important security checks.
- Test concurrency, retry safety, atomic deletion, and partial Auth/profile provisioning. Use a local environment where useful plus separate staging for hosted integration behavior.
- Release compatible schema/policy/functions before dependent UI changes; old browser clients may remain open, so compatibility matters. Keep secrets server-side, monitor denied operations/function errors/quotas, configure backups and test restoration according to the chosen plan, and maintain platform/client dependencies.
- Understanding check: if the browser may edit a customer's own request row, why is checking customer_id alone insufficient? Expected reasoning: the same customer could try changing worker_id or status to accepted; constrain fields and expose validated transitions rather than arbitrary updates.
- All three initial proposals have now been presented. Leave space for architecture 3 follow-ups before final comparison and recommendation. No final architecture choice yet.
- Official sources consulted: https://supabase.com/docs/guides/auth ; https://supabase.com/docs/guides/database/postgres/row-level-security ; https://supabase.com/docs/guides/database/functions ; https://supabase.com/docs/guides/functions .

## Final comparison and recommendation

- User requested a quick comparison of the three approaches.

| Criterion | Modular monolith | Microservices | Managed serverless backend |
| --- | --- | --- | --- |
| Initial development | Relatively straightforward; integrated framework | Highest coordination and infrastructure effort | Fast for standard workflows if team knows platform/SQL policies |
| Data consistency | Shared database transactions | Local transactions; cross-service coordination/retries | Shared PostgreSQL transactions; Auth/external API workflows still need coordination |
| Security implementation | Central server checks for roles and ownership | Checks in each service plus service identities and token handling | Database policies, restricted functions, and protected privileged credentials |
| Deployment and operations | One application plus database | Multiple services, databases, messaging, and monitoring | Less server administration; platform configuration and monitoring remain |
| Scaling | Replicate application; shared database constraint | Scale services independently; higher operating complexity | Provider manages function execution; database/quotas remain constraints |
| Main implementation difficulty | Concurrency, deletion rules, module boundaries | Partial failures, stale data, event delivery, compatible releases | Policy correctness, safe state transitions, distributed business logic |
| Fit for stated scope | Strong default | Weak justification without independent teams/scale requirements | Credible alternative if managed-platform approach suits the team |

- Recommendation: layered modular monolith using the proposed Django/PostgreSQL stack, with Render as one hosting option. This is the assistant's recommendation, not a user-confirmed selection.
- Assumptions: small team, ordinary initial traffic, browser-oriented workflows, no unstated independent-release or extreme availability requirements, and willingness to use Python/Django. Actual team skills, budget, traffic, and hosting constraints remain unknown.
- Rationale: profiles, requests, reviews, Q&A, and administrator operations share closely related data; local transactions and centralized business rules reduce coordination effort while still allowing modular code and multiple application instances.
- Serverless is a credible alternative when reducing infrastructure management is the priority and the team is comfortable with SQL/RLS and provider coupling. Microservices become more attractive with demonstrated needs for independent team ownership, releases, or uneven scaling; user count alone does not mandate them.
- All three initial walkthroughs and the requested quick comparison are complete. Requirement ambiguities remain explicitly unresolved and must be addressed before implementing affected business rules.

## Follow-up: large traffic and scaling risks

- User asked how each approach behaves under large traffic and whether any has particular problems.
- Traffic is a workload, not merely a registered-user count: distinguish worker/profile/review reads from request writes, hot workers receiving concurrent updates, sustained load from short bursts, and required response times. No numeric capacity claims are justified without instance sizes, query patterns, data volumes, and load tests.
- Modular monolith: run multiple stateless application instances behind a load balancer, use shared sessions, cache public catalogue/profile data, paginate/index queries, and serve static assets through a CDN. The shared database can become the bottleneck through expensive searches, connections, locks, or repeated queries. Read replicas can offload suitable reads but can lag; show current request state from an authoritative source. Replicating the full application for search-heavy traffic may be less resource-efficient than separately scaling catalogue services, but high traffic alone does not require microservices.
- Microservices: independently scale a catalogue service for read-heavy traffic while leaving requests/community smaller. Benefits require actual separation of resources/data and appropriate caching. Network fan-out, synchronous dependency chains, retry storms, broker/consumer backlog, duplicated caches, and expensive cross-service aggregation can degrade performance. Use bounded timeouts, limited retries with backoff/jitter, concurrency limits, and backpressure (limit or defer work rather than accepting unlimited load). Each service database can still bottleneck; queues absorb bursts only if consumers can eventually catch up and delayed processing is acceptable. Accepting a request needs authoritative local state, not a stale catalogue cache.
- Managed serverless: static UI delivery and provider-managed function concurrency can help with spikes, but many simultaneous functions can overwhelm the shared database or hit configured/platform quotas. Connection pooling reduces connection pressure, not underlying database computation or write contention. Indexed paginated reads, caching, set-based efficient RLS policies, bounded concurrency, and explicit overload behavior remain necessary. Function startup latency, runtime limits, Auth/API rate limits, and usage-driven cost are platform/plan-dependent risks, not quantified here. Current provider limits must be checked when choosing a plan. Never cache private responses across identities or skip policies for speed.
- Shared RentYourExpert example: many visitors browsing public worker pages are cache-friendly; many users mutating the same request require serialized/conditional authoritative updates regardless of architecture. If 10,000 customers submit distinct requests to one popular worker, these are separate rows, not necessarily a single-row write bottleneck; optional shared counters or worker-wide invariants can introduce contention.
- Caching public ratings/reviews permits some staleness only if acceptable; do not cache private request lists publicly. Indexes improve reads but add write/storage cost. Keep correctness checks for request state changes in the database.
- Recommendation remains monolith as the initial default under prior assumptions; measure first with realistic load tests and database/application metrics, optimize queries/cache, then add capacity or extract demonstrated hotspots. A sustained uneven workload plus independent ownership may justify microservices; a bursty workload and acceptable managed-platform constraints may favor serverless. No architecture automatically guarantees performance or low cost.

## Follow-up: when added complexity is justified

- User asked under what conditions microservices or serverless would justify their additional complexity.
- Decision principle: demonstrable benefits must outweigh development, security, deployment, and maintenance costs. Traffic alone and hypothetical future growth are insufficient evidence.
- Microservices become attractive when stable business boundaries align with independently responsible teams; coordinated releases demonstrably delay work; measured uneven workloads justify targeted scaling; or particular features need stronger resource/failure isolation. Teams must be equipped to version APIs/events, monitor distributed workflows, and recover partial failures. Synchronous dependencies and shared infrastructure can still undermine isolation.
- RentYourExpert example: catalogue/search and community traffic could be owned, deployed, and scaled separately while request state remains authoritative within the requests service. Extracting one proven hotspot can be sufficient; splitting every feature is unnecessary.
- Microservices are harder to justify when one small team handles tightly related workflows, most changes cross service boundaries, or the real bottleneck is inefficient database queries that splitting services will not fix.
- Managed serverless becomes attractive when a small team wants less server-operation work; managed Auth/data APIs substantially reduce development; workflows fit short function executions and database transactions; and the team can correctly implement/test RLS and privileged functions. Intermittent/bursty demand can be a favorable workload, but low traffic does not guarantee low cost.
- RentYourExpert example: profile/search reads, review/Q&A writes, and short request-state transitions fit the proposed managed backend. Auth/profile provisioning still requires explicit recovery from partial failures.
- Adoption conditions include checking actual plan quotas, latency behavior, data-location needs, recovery options, projected costs, and provider migration effort against project constraints. No plan-specific capacity or pricing is asserted here.
- Serverless is less attractive when workloads require long uninterrupted execution, strict control of runtime/infrastructure, or measured sustained-load costs are unfavorable. Background queues can adapt some long jobs but introduce further components.
- Microservices describe service/data boundaries; serverless describes managed execution. They can coexist, and a monolith can use a managed database. The three proposals are concrete designs, not mutually exclusive universal categories.
- Recommendation remains modular monolith without new evidence. Prefer the managed serverless proposal if reduced operations/productivity outweigh policy and provider costs; prefer microservices if independent teams/releases/scaling outweigh distributed coordination costs. User has not confirmed a final choice.

## Follow-up: expensive decisions to reverse

- User asked which decisions would be expensive to reverse later. Highest costs arise from accumulated production data, external/client contracts, and business rules spread across components; not every early decision needs to be finalized now.
- Identity/account model: separate customer and worker identities versus one account with role assignments affects login, references, permissions, and duplicate-account merging. Prefer stable internal account identifiers; model role/profile relationships explicitly without assuming dual roles are a confirmed requirement. Changing Auth providers can additionally require identity mapping, credential compatibility checks, and renewed sessions or password resets; do not assume password hashes are exportable/compatible.
- Data model and lifecycle/history: request states, review-to-request versus review-to-worker associations, account deletion, and retention rules become embedded in records and reporting. A later verified-review requirement cannot reliably establish which past reviews correspond to completed work if that evidence was never collected. Unnecessary personal data should not be collected simply for possible future flexibility. Deleted data cannot be reconstructed by a schema migration; retained backups are neither guaranteed recovery nor a substitute for an explicit retention policy.
- Microservice/data boundaries: moving tables into service-owned databases changes transactions into coordinated workflows and creates APIs/events plus operating infrastructure. Moving boundaries or recombining services requires data migration, contract changes, and coordinated releases. Begin with clear modules and extract only justified boundaries; a modular monolith is easier to extract than tangled code but extraction is not free.
- Provider coupling: direct frontend reliance on Supabase Auth/data APIs, RLS, and function conventions makes leaving the provider broader than moving PostgreSQL data. Reimplement authorization, identity flows, and deployed functions; PostgreSQL portability does not eliminate application coupling. Isolate platform calls in focused modules and keep schema/policies/functions in version control without building speculative generic abstractions.
- Framework/language and business-logic placement: rewriting a Django application or moving rules from Python to SQL/functions is costly when rules are scattered across views, admin hooks, frontend code, and triggers. Keep each business rule's authoritative implementation clear and use it from all write paths.
- Public APIs/event contracts: published field names, identifier meanings, and status values gain consumers. Once sent, historical events and older clients cannot be changed in place. Prefer additive evolution, deliberate versioning, and compatible migrations.
- Consistency promises: promising instant global account deletion or immediately fresh review averages while using asynchronous propagation creates a difficult mismatch. Specify authoritative sources and visible pending/error states; strengthen security-sensitive coordination where required.
- Comparatively reversible choices: application instance size/count, CSS styling, ordinary indexes (with migration/performance care), and moving a portable app to a similar host. Hosting changes can still involve database transfer, secrets, networking, cutover, and downtime planning; simpler does not mean free.
- Conclusion for RentYourExpert: prioritize account identities, request/review lifecycle, deletion policy, and data ownership before implementing affected flows. Keep deployment and infrastructure initially simple. Architecture recommendation remains provisional; no user-confirmed selection or new business requirements.
