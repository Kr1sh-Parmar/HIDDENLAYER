# Requirements Document

## Introduction

The Green Hydrogen Credit Marketplace is a blockchain-based platform that enables the trading and management of hydrogen production credits. The system allows certified hydrogen producers to issue credits (1 credit = 1kg H2 = 310 rupees), enables various stakeholders to purchase and manage these credits, and provides government and regulatory oversight capabilities. The platform integrates blockchain technology with traditional data storage and includes payment processing, user management, and regulatory compliance features.

## Requirements

### Requirement 1

**User Story:** As a certified hydrogen producer, I want to issue credits for my hydrogen production, so that I can monetize my clean energy production and participate in the carbon credit market.

#### Acceptance Criteria

1. WHEN a producer manufactures 1kg of hydrogen THEN the system SHALL allow them to issue 1 credit to the marketplace
2. WHEN a producer issues credits THEN the system SHALL record the transaction on the blockchain
3. WHEN credits are issued THEN the system SHALL update the producer's wallet balance
4. WHEN credits are issued THEN the system SHALL make them available in the net circulation for purchase
5. IF a producer is not certified THEN the system SHALL NOT allow credit issuance

### Requirement 2

**User Story:** As a factory owner, I want to buy hydrogen credits to meet my environmental quota, so that I can comply with pollution regulations and potentially receive benefits.

#### Acceptance Criteria

1. WHEN a factory purchases credits THEN the system SHALL transfer credits from circulation to their wallet
2. WHEN a factory purchases credits THEN the system SHALL process payment through the mock Razorpay gateway
3. WHEN a factory purchases credits THEN the system SHALL notify government and local pollution bodies
4. WHEN a factory sets a quota THEN the system SHALL track their progress toward meeting it
5. WHEN a factory meets their quota THEN the system SHALL notify state pollution bodies for certificate generation

### Requirement 3

**User Story:** As a government official, I want to monitor and manage user accounts, so that I can ensure compliance and prevent fraud in the credit system.

#### Acceptance Criteria

1. WHEN accessing the government dashboard THEN the system SHALL display options to freeze accounts, monitor usage, and audit accounts
2. WHEN a government official freezes an account THEN the system SHALL prevent that account from making transactions
3. WHEN monitoring usage THEN the system SHALL display real-time transaction data and wallet balances
4. WHEN auditing an account THEN the system SHALL provide AI-powered analysis (placeholder functionality)
5. WHEN any credit transaction occurs THEN the system SHALL automatically notify government entities

### Requirement 4

**User Story:** As a state pollution body official, I want to track factory compliance and issue certificates, so that I can reward compliant factories and enforce environmental regulations.

#### Acceptance Criteria

1. WHEN accessing the pollution body dashboard THEN the system SHALL display which factories have met their quotas
2. WHEN a factory meets quota requirements THEN the system SHALL generate a certificate with specific compliance codes
3. WHEN certificates are issued THEN the system SHALL record them for benefit eligibility tracking
4. WHEN viewing factory data THEN the system SHALL show current credit holdings and quota progress
5. WHEN factories exceed quotas THEN the system SHALL flag them for potential benefits

### Requirement 5

**User Story:** As a citizen, I want to purchase hydrogen credits, so that I can support clean energy and offset my carbon footprint.

#### Acceptance Criteria

1. WHEN a citizen wants to buy credits THEN the system SHALL provide a simple purchase interface
2. WHEN purchasing credits THEN the system SHALL process payment through the mock Razorpay gateway
3. WHEN credits are purchased THEN the system SHALL add them to the citizen's wallet
4. WHEN credits are purchased THEN the system SHALL update the public transaction history
5. IF payment fails THEN the system SHALL NOT transfer credits and SHALL display an error message

### Requirement 6

**User Story:** As any user of the system, I want to register and login securely, so that I can access my account and perform transactions safely.

#### Acceptance Criteria

1. WHEN a new user registers THEN the system SHALL create an account with their role (producer, factory, government, pollution body, citizen)
2. WHEN a user logs in THEN the system SHALL authenticate their credentials and redirect to appropriate dashboard
3. WHEN authentication fails THEN the system SHALL display an error message and prevent access
4. WHEN a user accesses protected pages THEN the system SHALL verify their login status
5. IF a user is not logged in THEN the system SHALL redirect them to the login page

### Requirement 7

**User Story:** As any stakeholder, I want to view transparent transaction history, so that I can verify the integrity and authenticity of credit transactions.

#### Acceptance Criteria

1. WHEN any transaction occurs THEN the system SHALL record it in both blockchain and transactions.json
2. WHEN viewing transaction history THEN the system SHALL display all public transactions with timestamps
3. WHEN a transaction is recorded THEN the system SHALL include sender, receiver, amount, and transaction type
4. WHEN accessing transaction data THEN the system SHALL ensure data consistency between blockchain and JSON storage
5. IF transactions.json doesn't exist THEN the system SHALL create it automatically

### Requirement 8

**User Story:** As a system administrator, I want the application to run easily in a single setup, so that deployment and maintenance are simplified.

#### Acceptance Criteria

1. WHEN running easy_run.py THEN the system SHALL create all necessary folders and files
2. WHEN easy_run.py executes THEN the system SHALL set up the virtual environment automatically
3. WHEN the setup completes THEN the system SHALL start the Flask application
4. WHEN the application starts THEN the system SHALL initialize blockchain connections and data files
5. IF any setup step fails THEN the system SHALL display clear error messages and stop execution