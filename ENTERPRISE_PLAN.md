# Enterprise Org/Tenant Model + SSO Plan

This document defines a minimal multi-tenant model and SSO plan suitable for corporate subscriptions.

## 1) Org/Tenant Data Model (shared DB, tenant-aware)

### Core Entities

**Organization**
- `id`, `name`, `slug`, `billing_email`, `status` (trial/active/suspended)
- `plan_tier`, `max_seats`, `seats_used`
- `created_at`, `updated_at`

**OrganizationDomain**
- `id`, `organization_id`, `domain`
- Used for auto-claiming users and SSO routing

**OrganizationMembership**
- `id`, `organization_id`, `user_id`
- `role` (owner, admin, manager, instructor, learner)
- `status` (invited/active/disabled)
- `created_at`, `updated_at`

**OrganizationInvite**
- `id`, `organization_id`, `email`, `role`, `invited_by`
- `token`, `expires_at`, `accepted_at`

**SeatSubscription**
- `id`, `organization_id`, `billing_cycle`, `seats_purchased`, `seats_used`
- `payment_provider`, `provider_subscription_id`

**LearningGroup (Cohorts/Teams)**
- `id`, `organization_id`, `name`, `manager_id`
- `created_at`, `updated_at`

**LearningGroupMembership**
- `id`, `learning_group_id`, `user_id`
- `role` (manager/member)

### Tenant Isolation
- Every course enrollment, order, and analytics record must include `organization_id`.
- Org admins only see their own org’s data.
- Superusers can access all orgs.

## 2) SSO Plan (SAML + OIDC)

### Providers
- **SAML 2.0** (Okta, Azure AD, OneLogin)
- **OIDC** (Google Workspace, Azure AD, Okta)

### SSO Data Model

**SSOProvider**
- `id`, `organization_id`, `provider_type` (saml/oidc)
- `issuer`, `sso_url`, `x509_cert` (for SAML)
- `client_id`, `client_secret`, `redirect_uri` (for OIDC)
- `email_domain`, `is_active`

### Authentication Flow
1) User enters email on login.
2) Match email domain to `OrganizationDomain`.
3) If org has SSO enabled, redirect to IdP.
4) On callback, map/auto-provision user + membership:
   - Create `User` if not exists.
   - Create `OrganizationMembership` with default role.
5) Issue JWT tokens and redirect to app.

### SCIM (Optional Phase 2)
- Support user provisioning/deprovisioning via SCIM 2.0.
- Store `scim_external_id` in `User` and `OrganizationMembership`.

### Compliance
- Audit log events: login, membership changes, SSO config changes.
- Periodic access reviews for org admins.

## 3) Implementation Notes
- Use `django-allauth` (OIDC) + `python3-saml` or `django-saml2-auth` for SAML.
- Add organization-aware permissions across APIs.
- Add org-level analytics dashboards and exports for compliance.
