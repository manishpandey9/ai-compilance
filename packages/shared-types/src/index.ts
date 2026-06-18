export const RISK_TIERS = [
  "prohibited",
  "high_risk",
  "limited_risk",
  "minimal_risk",
  "needs_review",
] as const;

export type RiskTier = (typeof RISK_TIERS)[number];

export const CLASSIFICATION_STATUSES = [
  "classified",
  "insufficient_information",
  "needs_expert_review",
  "conflicting_rules",
] as const;

export type ClassificationStatus = (typeof CLASSIFICATION_STATUSES)[number];

export const ACTOR_ROLES = [
  "provider",
  "deployer",
  "importer",
  "distributor",
  "authorised_representative",
] as const;

export type ActorRole = (typeof ACTOR_ROLES)[number];
