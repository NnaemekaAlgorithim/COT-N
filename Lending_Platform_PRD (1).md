**PRODUCT REQUIREMENTS DOCUMENT**

**Multi-Tenant Lending & Contribution Platform**

_Organization-based loan tracking and group savings, built for designers to prototype directly from_

**Important context for the designer**

This platform is for record-keeping and trust-based tracking only - it is NOT connected to any payment gateway, bank, or financial transaction system.

All money referenced (principal, loans, contributions, interest) moves in real life between people who already know and trust each other. The app exists purely to track who owes what, who has paid what, and to create transparency and accountability within a group.

Every "record as granted", "mark as received", or "acknowledge" action is a manual confirmation step by a human - not an automated transfer.

# **1\. Platform Overview**

This is a multi-tenant platform where independent groups - referred to as Organizations - can each run their own internal lending circle and/or contribution (group savings) scheme. Each Organization operates independently with its own members, its own principal capital, its own interest rules, and its own loan and contribution history.

Examples of Organizations that would use this platform: a cooperative thrift society, a family lending circle, a workplace savings group, or a community money-lending club.

## **1.1 Subscription Model**

**Paid access - no free tier**

Before a user can create an Organization, they must complete a recurring monthly subscription payment of ₦2,000 via Paystack.

There is no free trial. Every single Organization on the platform, regardless of size or activity level, must be on an active paid subscription to remain usable.

The subscription is tied to the Organization itself, not to the individual user - a user who creates three Organizations pays ₦2,000 per month for each one independently.

Any admin or founder can make payment for the monthly subscription, and if a renewal payment fails, the whole system becomes view only for everyone but making subscription is possible.

## **1.2 Core Concepts**

| **Term**            | **Definition**                                                                                                       |
| ------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Organization        | A self-contained tenant on the platform with its own members, capital, loans, and contributions.                     |
| Founder             | The user who created the Organization. Has full control by default and certain powers no one else can have.          |
| Admin               | A member promoted by the Founder. Can approve loans and acknowledge contributions, but cannot add principal capital. |
| Member              | Any user who has joined an Organization. Can request loans and make contributions.                                   |
| Principal Capital   | The lending pool of the Organization. Only the Founder can add to it.                                                |
| Loan Tenure         | The repayment period of a loan, which only starts counting once the borrower confirms receipt.                       |
| Contribution Period | A recurring interval (e.g. monthly) set by the Founder during which members are expected to contribute a set amount. |

# **2\. Roles and Permissions**

There are three roles within any single Organization. A user can hold different roles in different Organizations - for example, being a Founder of one group and an ordinary Member of another.

## **2.1 Role Permission Matrix**

| **Capability**                            | **Founder**        | **Admin**      | **Member**   |
| ----------------------------------------- | ------------------ | -------------- | ------------ |
| Create an Organization                    | ✓ (by creating it) | -              | -            |
| Add / increase principal capital          | ✓ Only             | ✗              | ✗            |
| Promote a member to Admin                 | ✓                  | ✗              | ✗            |
| Set interest rate per tenure              | ✓                  | ✗              | ✗            |
| Set defaulter penalty (per day)           | ✓                  | ✗              | ✗            |
| Set contribution period & amount          | ✓                  | ✗              | ✗            |
| Set contribution fine rules               | ✓                  | ✗              | ✗            |
| Approve a loan request                    | ✓                  | ✓              | ✗            |
| Send approved loan (final release)        | ✓ Only             | ✗              | ✗            |
| Request a loan                            | ✓                  | ✓              | ✓            |
| Mark loan as received                     | ✓ (own loan)       | ✓ (own loan)   | ✓ (own loan) |
| Make a contribution                       | ✓                  | ✓              | ✓            |
| Acknowledge a contribution                | ✓                  | ✓              | ✗            |
| Approve / reject a join request           | ✓ (casts vote)     | ✓ (casts vote) | ✗            |
| Search and join an Organization           | ✓ (any user)       | ✓ (any user)   | ✓ (any user) |
| Transfer Founder role to an Admin         | ✓ Only             | ✗              | ✗            |
| Leave the Organization (no pending loans) | ✓                  | ✓              | ✓            |
| Pay Organization subscription (Paystack)  | ✓                  | ✓              | ✗            |

## **2.2 Important Role Rule**

**Founder-only powers**

Two actions are reserved exclusively for the Founder and cannot be delegated to Admins:

1\. Adding or increasing the principal capital of the Organization.

2\. Performing the final "send" action that releases an approved loan to the requester.

Admins can approve a loan request, but the Founder must still personally release it before the borrower can mark it as received.

# **3\. Organization Lifecycle**

## **3.1 Creating an Organization**

1. Any registered user can initiate creating a new Organization from the platform.
2. Before the Organization becomes active and usable, the creator must complete a ₦2,000 monthly subscription payment via Paystack. The Organization does not exist in a usable state until this payment succeeds.
3. Upon successful payment, the creator is automatically assigned the Founder role for that Organization.
4. The Founder sets up the Organization profile: name, description, and visibility (so other users can find it).
5. The subscription renews monthly. (notify Founder 3 days before renewal) and the grace period 0f 3days if renewal fails.

## **3.2 Discovering and Joining an Organization**

1. Other users can search the platform for Organizations by name.
2. A user submits a request to join an Organization they find.
3. The Founder or any Admin can cast an approve / reject decision on the join request.
4. Majority decision rules: once enough Admins (and/or the Founder) have voted that a clear majority is reached either way, the request is immediately resolved - it does not need to wait for every single Admin to vote.
5. Tie-breaker rule: if votes are evenly split 50/50 among those who have voted, the Founder's vote is the deciding vote, regardless of how many Admins voted either way.
6. The requesting user receives a real-time notification of the final outcome - approved or rejected.

**Worked example for the designer**

An Organization has 4 Admins plus the Founder. A join request comes in.

If 3 of the 4 Admins vote Approve before the 4th votes, the request is resolved immediately as APPROVED - majority reached, no need to wait on the last Admin.

If the vote ends up 2 Approve / 2 Reject among the Admins (a tie), the system waits for the Founder's vote, which then decides the outcome regardless of the 2-2 split.

## **3.3 Promoting Members to Admin**

1. The Founder can promote any member, or multiple members, to the Admin role.
2. The Founder can also demote an Admin back to Member status.
3. There is no limit specified on the number of Admins an Organization can have.

## **3.4 Founder Role Transfer & Leaving the Organization**

1. A Founder can transfer the Founder role to any existing Admin within the Organization.
2. A Founder can only leave the Organization if they have no pending (unresolved/unpaid) loans of their own at the time.
3. This same rule applies to every member: any user with an outstanding pending loan cannot leave the Organization until that loan is fully repaid or otherwise resolved.
4. If a Founder transfers their role and then leaves, the newly promoted Founder inherits all Founder-only powers (principal capital control, final loan release, role transfer).

# **4\. Loan Request & Approval Flow**

## **4.1 Loan Lifecycle - Status Flow**

Every loan request moves through five distinct states. The designer should treat each state as a distinct visual indicator (badge/chip) shown to all relevant parties.

| **1\. REQUESTED** | **2\. PENDING APPROVAL** | **3\. APPROVED (majority)** | **4\. SENT BY FOUNDER** | **5\. RECEIVED - TENURE STARTS** |
| ----------------- | ------------------------ | --------------------------- | ----------------------- | -------------------------------- |

_Alternative end state - if the majority/tie-break vote results in rejection:_

| **2\. PENDING APPROVAL** | **REJECTED (majority or Founder tie-break)** |
| ------------------------ | -------------------------------------------- |

## **4.2 Step-by-Step Loan Flow**

1. A Member (including Admins and the Founder) submits a loan request specifying the amount requested from the principal capital.
2. The loan enters PENDING status. All Admins in the Organization are notified.
3. Each Admin casts an approve / reject decision. Majority decision rules apply - once a clear majority is reached either way, the request is resolved without needing every Admin to vote.
4. If the Admin vote ends in a 50/50 tie, the Founder's decision is the deciding vote.
5. If the final outcome is REJECTED, the requester is notified and the loan process ends. They may submit a new request later.
6. If the final outcome is APPROVED, the request becomes visible to the Founder for the final release step.
7. The Founder clicks Send. This is the action that formally marks the loan as released from the principal capital.
8. The requester receives a real-time notification that the loan has been sent.
9. The requester must manually click Received to confirm. This is the moment the loan tenure begins counting - not the moment it was sent.

**Why the "Received" click matters**

Because this system tracks money exchanged in person (cash, bank transfer outside the app, etc.), there can be a delay between the Founder marking a loan as "sent" and the borrower actually getting the money in hand.

The tenure clock (and therefore interest and default calculations) must only start once the borrower confirms they physically have the funds - otherwise the borrower could be unfairly charged interest for days they never had access to the money.

## **4.3 Interest, Tenure, and Default Rules**

| **Setting**              | **Configured by** | **Description**                                                                                                                                             |
| ------------------------ | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Loan tenure length       | Founder           | Set ONCE for the entire Organization - every loan request within this Organization uses the same fixed tenure length. Not configurable per individual loan. |
| Interest rate per tenure | Founder           | A percentage rate applied across the fixed Organization-wide tenure (e.g. "5% over 30 days").                                                               |
| Defaulter penalty rate   | Founder           | An additional percentage added for every day the loan remains unpaid past the tenure end date.                                                              |

## **4.4 Repayment Rule**

**Full repayment only**

Loan repayment must be made in full in a single transaction record - the platform does not support partial or instalment-based repayment.

The designer should design the repayment screen as a single confirmation action showing the total amount due (principal + interest + any accrued default penalty), not an instalment input field.

## **4.5 Repayment Notifications**

- Real-time notifications must be sent to the borrower as repayment (with interest) becomes due.
- Real-time notifications must be sent to Admins/Founder when a repayment is logged.

# **5\. Contribution (Group Savings) Module**

## **5.1 Contribution Lifecycle - Status Flow**

Every contribution submitted by a member moves through three states before it is considered fully settled.

| **1\. CONTRIBUTION MADE** | **2\. IN PROGRESS (awaiting acknowledgement)** | **3\. ACKNOWLEDGED BY ALL ADMINS** |
| ------------------------- | ---------------------------------------------- | ---------------------------------- |

## **5.2 Step-by-Step Contribution Flow**

1. The Founder sets the contribution period (e.g. monthly, weekly, or any custom interval) and the expected contribution amount for the Organization.
2. Every member receives a notification at the start of each contribution period, reminding them their contribution is due.
3. A member makes their contribution and marks it as submitted within the app. Status becomes IN PROGRESS.
4. All Admins must acknowledge the contribution as received before it is marked complete.
5. Special case: If the Founder is the one contributing, Admins still acknowledge it - the Founder cannot self-acknowledge their own contribution.
6. Special case: If an Admin is the one contributing, the remaining Admins acknowledge it.
7. Fallback rule: If the Organization has no Admins at all (only a Founder and Members), the Founder alone has the authority to acknowledge every contribution, including their own submissions and members' submissions.

**Edge case the designer must account for**

An Organization can exist in a state with zero Admins (only a Founder + Members). The acknowledgement flow must adapt: with no Admins present, the Founder becomes the sole approver for both loans and contributions.

Design the empty-state and the acknowledgement screen to detect this condition and change the required approver(s) accordingly.

## **5.3 Contribution Penalties**

**Contribution fine formula**

The Founder can optionally enable a fine for late or missed contributions.

The fine is calculated as a percentage of the expected contribution amount (set by the Founder), applied per custom interval that the Founder also defines (e.g. "2% of the contribution amount added every 3 days the member remains in default").

This mirrors the loan defaulter penalty structure - both are percentage-based and accrue over a repeating time interval rather than being a single flat fee.

# **6\. Notification Requirements**

Real-time notifications are a core requirement across both modules. The table below consolidates every notification trigger mentioned or implied in the requirements, for the designer to account for in the notification centre / inbox design.

| **Trigger Event**                                        | **Notified Party**                   | **Module**   |
| -------------------------------------------------------- | ------------------------------------ | ------------ |
| A loan request is submitted                              | All Admins                           | Loan         |
| A loan is fully approved by all Admins                   | Founder                              | Loan         |
| A loan is sent by the Founder                            | Requesting Member                    | Loan         |
| A loan repayment becomes due (with interest)             | Borrower                             | Loan         |
| A loan repayment is logged                               | Admins / Founder                     | Loan         |
| A loan is overdue (defaulting)                           | Borrower, Admins, Founder            | Loan         |
| A new contribution period opens                          | All Members                          | Contribution |
| A contribution is submitted                              | All Admins (or Founder if no Admins) | Contribution |
| A contribution is acknowledged by all required approvers | Contributing Member                  | Contribution |
| A contribution is late or missed (if fine is enabled)    | Contributing Member, Admins          | Contribution |

# **7\. Suggested Screen List for Prototyping**

_This is not part of the original requirements but is provided to help structure the Figma file into logical screens / frames._

## **7.1 Onboarding, Subscription & Organization**

- Sign up / Login
- Organization search & discovery
- Organization profile / join request screen
- Join request vote screen - Founder and Admin side (shows current vote tally, approve/reject buttons, tie-break indicator when Founder vote is needed)
- Create Organization form
- Paystack subscription payment screen (₦2,000 per month - no free trial messaging must be clear here)
- Subscription status screen (shows renewal date, payment history, renewal failure state)
- Organization dashboard (overview of principal capital, members, active loans, contribution status)
- Member management screen (promote/demote Admin, Founder transfer - Founder only)
- Founder role transfer confirmation screen
- Leave Organization screen (blocked with explanation if user has pending loans)

## **7.2 Loan Module**

- Loan request form
- Loan status tracker (showing the 5-stage approval flow plus the rejected end-state visually)
- Admin vote screen (shows current vote tally, approve/reject buttons, tie-break indicator when Founder's deciding vote is awaited)
- Loan rejected notification screen (shown to requester)
- Founder "send loan" confirmation screen
- "Mark as received" confirmation screen (borrower side - with clear messaging that tenure starts the moment they confirm)
- Repayment screen - full repayment only, showing total due: principal + interest + any accrued default penalty in clear breakdown
- Loan history / past loans list
- Organization-wide loan settings screen (tenure length, interest rate, defaulter penalty rate - Founder only)

## **7.3 Contribution Module**

- Contribution settings screen (period, amount, fine rules - Founder only)
- Make a contribution screen
- Contribution acknowledgement queue (Admin/Founder side)
- Contribution history per member
- Organization-wide contribution summary

## **7.4 Notifications**

- Notification centre / inbox
- Individual notification detail / action screen