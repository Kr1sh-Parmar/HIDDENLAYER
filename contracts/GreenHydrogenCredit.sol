// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract GreenHydrogenCredit is ERC20, Ownable {
    // Structs for role management and quota tracking
    struct Producer {
        bool certified;
        uint256 totalIssued;
        uint256 lastIssuanceTime;
        bool isActive;
    }
    
    struct Factory {
        uint256 quota;
        bool hasQuota;
        uint256 creditsPurchased;
        bool quotaMet;
        uint256 quotaSetTime;
    }
    
    // Role definitions
    enum UserRole { NONE, PRODUCER, FACTORY, GOVERNMENT, POLLUTION_BODY, CITIZEN }
    
    // State variables
    mapping(address => Producer) public producers;
    mapping(address => Factory) public factories;
    mapping(address => bool) public isFrozen;
    mapping(address => UserRole) public userRoles;
    mapping(address => string) public userRoleNames;
    
    // Government and regulatory addresses
    address public governmentAddress;
    address public pollutionBodyAddress;
    
    // Events for comprehensive tracking
    event AccountFrozen(address indexed user, bool frozen);
    event CreditIssued(address indexed producer, uint256 amount, uint256 timestamp);
    event CreditPurchased(address indexed buyer, address indexed seller, uint256 amount, uint256 price, uint256 timestamp);
    event ProducerCertified(address indexed producer, bool certified);
    event QuotaSet(address indexed factory, uint256 quota, uint256 timestamp);
    event QuotaMet(address indexed factory, uint256 totalPurchased, uint256 timestamp);
    event RoleAssigned(address indexed user, UserRole role, string roleName);
    event RegulatoryNotification(address indexed notifier, address indexed subject, string action, uint256 timestamp);

    constructor() ERC20("Green Hydrogen Credit", "GHC") {
        // Set deployer as government by default
        governmentAddress = msg.sender;
        userRoles[msg.sender] = UserRole.GOVERNMENT;
        userRoleNames[msg.sender] = "government";
        emit RoleAssigned(msg.sender, UserRole.GOVERNMENT, "government");
    }

    // Modifiers for role-based access control
    modifier onlyGovernment() {
        require(msg.sender == governmentAddress || userRoles[msg.sender] == UserRole.GOVERNMENT, "Only government can perform this action");
        _;
    }
    
    modifier onlyPollutionBody() {
        require(msg.sender == pollutionBodyAddress || userRoles[msg.sender] == UserRole.POLLUTION_BODY, "Only pollution body can perform this action");
        _;
    }
    
    modifier onlyCertifiedProducer() {
        require(userRoles[msg.sender] == UserRole.PRODUCER && producers[msg.sender].certified && producers[msg.sender].isActive, "Only certified active producers can perform this action");
        _;
    }
    
    modifier onlyFactory() {
        require(userRoles[msg.sender] == UserRole.FACTORY, "Only factories can perform this action");
        _;
    }
    
    modifier notFrozen(address account) {
        require(!isFrozen[account], "Account is frozen");
        _;
    }

    // --- Government-Only Functions ---
    function setGovernmentAddress(address _government) public onlyOwner {
        governmentAddress = _government;
        userRoles[_government] = UserRole.GOVERNMENT;
        userRoleNames[_government] = "government";
        emit RoleAssigned(_government, UserRole.GOVERNMENT, "government");
    }
    
    function setPollutionBodyAddress(address _pollutionBody) public onlyGovernment {
        pollutionBodyAddress = _pollutionBody;
        userRoles[_pollutionBody] = UserRole.POLLUTION_BODY;
        userRoleNames[_pollutionBody] = "pollution_body";
        emit RoleAssigned(_pollutionBody, UserRole.POLLUTION_BODY, "pollution_body");
    }
    
    function assignRole(address user, UserRole role, string memory roleName) public onlyGovernment {
        userRoles[user] = role;
        userRoleNames[user] = roleName;
        emit RoleAssigned(user, role, roleName);
    }
    
    function certifyProducer(address producer, bool certified) public onlyGovernment {
        require(userRoles[producer] == UserRole.PRODUCER, "Address must be registered as producer");
        producers[producer].certified = certified;
        producers[producer].isActive = certified;
        emit ProducerCertified(producer, certified);
        emit RegulatoryNotification(msg.sender, producer, certified ? "CERTIFIED" : "DECERTIFIED", block.timestamp);
    }
    
    function setAccountFrozen(address user, bool frozen) public onlyGovernment {
        isFrozen[user] = frozen;
        emit AccountFrozen(user, frozen);
        emit RegulatoryNotification(msg.sender, user, frozen ? "FROZEN" : "UNFROZEN", block.timestamp);
    }

    // --- Producer Functions ---
    function registerAsProducer() public {
        require(userRoles[msg.sender] == UserRole.NONE, "User already has a role assigned");
        userRoles[msg.sender] = UserRole.PRODUCER;
        userRoleNames[msg.sender] = "producer";
        producers[msg.sender] = Producer({
            certified: false,
            totalIssued: 0,
            lastIssuanceTime: 0,
            isActive: false
        });
        emit RoleAssigned(msg.sender, UserRole.PRODUCER, "producer");
    }
    
    function issueCredits(uint256 amount) public onlyCertifiedProducer notFrozen(msg.sender) {
        require(amount > 0, "Amount must be greater than 0");
        
        _mint(msg.sender, amount);
        producers[msg.sender].totalIssued += amount;
        producers[msg.sender].lastIssuanceTime = block.timestamp;
        
        emit CreditIssued(msg.sender, amount, block.timestamp);
        
        // Notify government and pollution body
        if (governmentAddress != address(0)) {
            emit RegulatoryNotification(msg.sender, governmentAddress, "CREDIT_ISSUED", block.timestamp);
        }
        if (pollutionBodyAddress != address(0)) {
            emit RegulatoryNotification(msg.sender, pollutionBodyAddress, "CREDIT_ISSUED", block.timestamp);
        }
    }
    
    // --- Factory Functions ---
    function registerAsFactory() public {
        require(userRoles[msg.sender] == UserRole.NONE, "User already has a role assigned");
        userRoles[msg.sender] = UserRole.FACTORY;
        userRoleNames[msg.sender] = "factory";
        factories[msg.sender] = Factory({
            quota: 0,
            hasQuota: false,
            creditsPurchased: 0,
            quotaMet: false,
            quotaSetTime: 0
        });
        emit RoleAssigned(msg.sender, UserRole.FACTORY, "factory");
    }
    
    function setQuota(uint256 quota) public onlyFactory {
        require(quota > 0, "Quota must be greater than 0");
        factories[msg.sender].quota = quota;
        factories[msg.sender].hasQuota = true;
        factories[msg.sender].quotaSetTime = block.timestamp;
        factories[msg.sender].quotaMet = false;
        emit QuotaSet(msg.sender, quota, block.timestamp);
    }
    
    function purchaseCredits(address seller, uint256 amount, uint256 price) public payable notFrozen(msg.sender) notFrozen(seller) {
        require(amount > 0, "Amount must be greater than 0");
        require(balanceOf(seller) >= amount, "Seller has insufficient credits");
        
        // Transfer credits from seller to buyer
        _transfer(seller, msg.sender, amount);
        
        // Update factory purchase tracking if buyer is a factory
        if (userRoles[msg.sender] == UserRole.FACTORY) {
            factories[msg.sender].creditsPurchased += amount;
            
            // Check if quota is met
            if (factories[msg.sender].hasQuota && 
                factories[msg.sender].creditsPurchased >= factories[msg.sender].quota && 
                !factories[msg.sender].quotaMet) {
                factories[msg.sender].quotaMet = true;
                emit QuotaMet(msg.sender, factories[msg.sender].creditsPurchased, block.timestamp);
                
                // Notify pollution body about quota completion
                if (pollutionBodyAddress != address(0)) {
                    emit RegulatoryNotification(msg.sender, pollutionBodyAddress, "QUOTA_MET", block.timestamp);
                }
            }
        }
        
        emit CreditPurchased(msg.sender, seller, amount, price, block.timestamp);
        
        // Notify government and pollution body of purchase
        if (governmentAddress != address(0)) {
            emit RegulatoryNotification(msg.sender, governmentAddress, "CREDIT_PURCHASED", block.timestamp);
        }
        if (pollutionBodyAddress != address(0)) {
            emit RegulatoryNotification(msg.sender, pollutionBodyAddress, "CREDIT_PURCHASED", block.timestamp);
        }
    }
    
    // --- Citizen Functions ---
    function registerAsCitizen() public {
        require(userRoles[msg.sender] == UserRole.NONE, "User already has a role assigned");
        userRoles[msg.sender] = UserRole.CITIZEN;
        userRoleNames[msg.sender] = "citizen";
        emit RoleAssigned(msg.sender, UserRole.CITIZEN, "citizen");
    }
    
    // --- View Functions ---
    function getProducerInfo(address producer) public view returns (Producer memory) {
        return producers[producer];
    }
    
    function getFactoryInfo(address factory) public view returns (Factory memory) {
        return factories[factory];
    }
    
    function getUserRole(address user) public view returns (UserRole, string memory) {
        return (userRoles[user], userRoleNames[user]);
    }
    
    function isAccountFrozen(address account) public view returns (bool) {
        return isFrozen[account];
    }
    
    // --- Modified Core Functions ---
    function _beforeTokenTransfer(address from, address to, uint256 amount) internal override {
        require(!isFrozen[from], "ERC20: sender account is frozen");
        require(!isFrozen[to], "ERC20: recipient account is frozen");
        super._beforeTokenTransfer(from, to, amount);
    }
    
    // Override transfer functions to emit regulatory notifications
    function transfer(address to, uint256 amount) public override notFrozen(msg.sender) notFrozen(to) returns (bool) {
        bool result = super.transfer(to, amount);
        if (result) {
            emit RegulatoryNotification(msg.sender, governmentAddress, "TRANSFER", block.timestamp);
        }
        return result;
    }
    
    function transferFrom(address from, address to, uint256 amount) public override notFrozen(from) notFrozen(to) returns (bool) {
        bool result = super.transferFrom(from, to, amount);
        if (result) {
            emit RegulatoryNotification(from, governmentAddress, "TRANSFER", block.timestamp);
        }
        return result;
    }
}