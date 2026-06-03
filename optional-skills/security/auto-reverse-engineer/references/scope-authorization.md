# Scope and Authorization

Before analysis, record in `authorization.md` and `scope.txt`:

1. Right to analyze: owner/author/purchase/written authorization/bug bounty/
   research agreement.
2. User affirms lawfulness: jurisdiction, anti-circumvention, license, ToS,
   contract.
3. Exact scope: artifacts, devices, hosts, accounts, live interaction. Default
   live interaction: no.

Proceed only when all three are clear. Ask once for missing details; then refuse
if still unclear. Runtime out-of-scope pivots become inbox authorization
requests, never unilateral action.

```markdown
# Authorization Record - <slug>
- date: YYYY-MM-DD
- operator: <user identity>
- target: <name + sha256 per artifact>
- basis: owner | written-authorization | bug-bounty | research-agreement | other
- jurisdiction affirmed lawful: yes
- live interaction permitted: no | yes - [devices/hosts/accounts]
- notes: <verbatim statement>
```
