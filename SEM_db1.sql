DROP TABLE EnglishQualification;
DROP TABLE TertiaryQualification;
DROP TABLE PreUniSubject;
DROP TABLE PreUniQualification;
DROP TABLE QualificationSubject;
DROP TABLE ProgrammeInCharge;
DROP TABLE ProgrammeCourse;
DROP TABLE ApplicationProgramme;
DROP TABLE Applications;
DROP TABLE Course;
DROP TABLE Enquiry;
DROP TABLE Academician;
DROP TABLE LoginSession;
DROP TABLE Account;
DROP TABLE ProgrammeCampus;
DROP TABLE Programme;
DROP TABLE Intake;
DROP TABLE Campus;


CREATE TABLE `Account`(
    `accountID` INT AUTO_INCREMENT NOT NULL,
    `accEmail` VARCHAR(50) NOT NULL,
    `accPassword` VARCHAR(50) NOT NULL,
    `accType` VARCHAR(20) NOT NULL,
    `accStatus` VARCHAR(20) NOT NULL,
    `fullName` VARCHAR(80) NULL,
    `identification` VARCHAR(20) NULL,
    `gender` VARCHAR(10) NULL,
    `fullAddress` VARCHAR(200) NULL,
    `handphoneNumber` VARCHAR(20) NULL,
    PRIMARY KEY(`accountID`)
)
COLLATE='latin1_swedish_ci'
ENGINE=InnoDB;

CREATE TABLE `LoginSession`(
    `loginSessionID` INT AUTO_INCREMENT NOT NULL,
    `ipAddress` VARCHAR(200) NOT NULL,
    `loginTime` DATETIME NOT NULL,
    `logoutTime` DATETIME,
    `accountID` INT NOT NULL,
    PRIMARY KEY (`loginSessionID`),
	CONSTRAINT `fk_accountID3` FOREIGN KEY (`accountID`) REFERENCES `Account` (`accountID`) ON UPDATE RESTRICT ON DELETE CASCADE
)
COLLATE='latin1_swedish_ci'
ENGINE=InnoDB;

CREATE TABLE `Intake`(
    `intakeID` VARCHAR(10) NOT NULL,
    `intakeName` VARCHAR(50) NOT NULL,
    `intakeYear` INT NOT NULL,
    `intakeMonth` INT NOT NULL,
    PRIMARY KEY(`intakeID`)
)
COLLATE='latin1_swedish_ci'
ENGINE=InnoDB
;

CREATE TABLE `Programme`(
    `programmeID` VARCHAR(10) NOT NULL,
    `programmeName` VARCHAR(80) NOT NULL,
    `programmeDescription` VARCHAR(400) NOT NULL,
    `programmeDuration` INT NOT NULL,
    `programmeType` VARCHAR(20) NOT NULL,
    PRIMARY KEY(`programmeID`)
)
COLLATE='latin1_swedish_ci'
ENGINE=InnoDB
;

CREATE TABLE `Campus`(
    `campusID` VARCHAR(10) NOT NULL,
    `campusName` VARCHAR(80) NOT NULL,
    `campusLocation` VARCHAR(200) NOT NULL,
    `campusURL` VARCHAR(200),
    PRIMARY KEY(`campusID`)
)
COLLATE='latin1_swedish_ci'
ENGINE=InnoDB
;

CREATE TABLE `Course`(
    `courseCode` VARCHAR(10) NOT NULL,
    `courseName` VARCHAR(80) NOT NULL,
    `courseDescription` VARCHAR(400) NOT NULL,
    PRIMARY KEY (`courseCode`)
)
COLLATE='latin1_swedish_ci'
ENGINE=InnoDB
;

CREATE TABLE `Academician`(
    `academicianID` VARCHAR(10) NOT NULL,
    `academicianName` VARCHAR(100) NOT NULL,
    `academicianTitle` VARCHAR(50) NOT NULL,
    `academicianEmail` VARCHAR(50) NOT NULL,
    `designation` VARCHAR(50) NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `educationBackground` VARCHAR(200) NOT NULL,
    `publication` VARCHAR(400),
    `researchArea` VARCHAR(200),
    `organizationMembership` VARCHAR(200),
    `academicianURL` VARCHAR(200),
    PRIMARY KEY(`academicianID`)
)
COLLATE='latin1_swedish_ci'
ENGINE=InnoDB
;

CREATE TABLE `Enquiry`(
    `enquiryID` INT AUTO_INCREMENT NOT NULL,
    `enquiryTopic` VARCHAR(50) NOT NULL,
    `enquiryTitle` VARCHAR(100) NOT NULL,
    `question` VARCHAR(400) NOT NULL,
    `enquiryImagePath` VARCHAR(100),
    `datetimeEnquire` DATETIME NOT NULL,
    `enquiryStatus` VARCHAR(50) NOT NULL,
    `response` VARCHAR(400),
    `responseImagePath` VARCHAR(100),
    `datetimeResponse` DATETIME,
    `enquiryAccountID` INT NOT NULL,
    `responseAccountID` INT,
    PRIMARY KEY (`enquiryID`),
    INDEX `fk_enquiryAccountID` (`enquiryAccountID`) USING BTREE,
  INDEX `fk_responseAccountID` (`responseAccountID`) USING BTREE,
	CONSTRAINT `fk_enquiryAccountID` FOREIGN KEY (`enquiryAccountID`) REFERENCES `Account` (`accountID`) ON UPDATE RESTRICT ON DELETE CASCADE,
	CONSTRAINT `fk_responseAccountID` FOREIGN KEY (`responseAccountID`) REFERENCES `Account` (`accountID`) ON UPDATE RESTRICT ON DELETE CASCADE
)
COLLATE='latin1_swedish_ci'
ENGINE=InnoDB
;

CREATE TABLE `QualificationSubject`(
    `qualificationSubjectID` VARCHAR(20) NOT NULL,
    `subjectName` VARCHAR(50) NOT NULL,
    `grade` VARCHAR(10),
    `qualificationName` VARCHAR(50) NOT NULL,
    `programmeID` VARCHAR(10) NOT NULL,
    PRIMARY KEY(`qualificationSubjectID`),
    INDEX `fk_programmeID` (`programmeID`) USING BTREE,
	CONSTRAINT `fk_programmeID` FOREIGN KEY (`programmeID`) REFERENCES `Programme` (`programmeID`) ON UPDATE RESTRICT ON DELETE CASCADE
)
COLLATE='latin1_swedish_ci'
ENGINE=InnoDB
;

CREATE TABLE `ProgrammeCourse`(
    `programmeCourseID` VARCHAR(25) NOT NULL,
    `creditHour` INT NOT NULL,
    `courseCode` VARCHAR(10) NOT NULL,
    `programmeID` VARCHAR(10) NOT NULL,
    PRIMARY KEY(`programmeCourseID`),
    INDEX `fk_courseCode` (`courseCode`) USING BTREE,
  INDEX `fk_programmeID2` (`programmeID`) USING BTREE,
	CONSTRAINT `fk_courseCode` FOREIGN KEY (`courseCode`) REFERENCES `Course` (`courseCode`) ON UPDATE RESTRICT ON DELETE CASCADE,
	CONSTRAINT `fk_programmeID2` FOREIGN KEY (`programmeID`) REFERENCES `Programme` (`programmeID`) ON UPDATE RESTRICT ON DELETE CASCADE
)
COLLATE='latin1_swedish_ci'
ENGINE=InnoDB
;

CREATE TABLE `ProgrammeCampus`(
    `programmeCampusID` VARCHAR(10) NOT NULL,
    `startDate` DATETIME NOT NULL,
    `programmeID` VARCHAR(10) NOT NULL,
    `campusID` VARCHAR(10) NOT NULL,
    `intakeID` VARCHAR(10) NOT NULL,
    PRIMARY KEY(`programmeCampusID`),
    INDEX `fk_campusID` (`campusID`) USING BTREE,
  INDEX `fk_programmeID3` (`programmeID`) USING BTREE,
  INDEX `fk_intakeID` (`intakeID`) USING BTREE,
	CONSTRAINT `fk_campusID` FOREIGN KEY (`campusID`) REFERENCES `Campus` (`campusID`) ON UPDATE RESTRICT ON DELETE CASCADE,
	CONSTRAINT `fk_programmeID3` FOREIGN KEY (`programmeID`) REFERENCES `Programme` (`programmeID`) ON UPDATE RESTRICT ON DELETE CASCADE,
	CONSTRAINT `fk_intakeID` FOREIGN KEY (`intakeID`) REFERENCES `Intake` (`intakeID`) ON UPDATE RESTRICT ON DELETE CASCADE
)
COLLATE='latin1_swedish_ci'
ENGINE=InnoDB
;

CREATE TABLE `ProgrammeInCharge`(
    `programmeInChargeID` VARCHAR(10) NOT NULL,
    `programmeCampusID` VARCHAR(10) NOT NULL,
    `academicianID` VARCHAR(10) NOT NULL,
    PRIMARY KEY(`ProgrammeInChargeID`),
    INDEX `fk_programmeCampusID` (`programmeCampusID`) USING BTREE,
   INDEX `fk_academicianID` (`academicianID`) USING BTREE,
	CONSTRAINT `fk_programmeCampusID` FOREIGN KEY (`programmeCampusID`) REFERENCES `ProgrammeCampus` (`programmeCampusID`) ON UPDATE RESTRICT ON DELETE CASCADE,
	CONSTRAINT `fk_academicianID` FOREIGN KEY (`academicianID`) REFERENCES `Academician` (`academicianID`) ON UPDATE RESTRICT ON DELETE CASCADE
)
COLLATE='latin1_swedish_ci'
ENGINE=InnoDB
;

CREATE TABLE `Applications`(
    `applicationID` INT AUTO_INCREMENT NOT NULL,
    `studentName` VARCHAR(80),
    `identification` VARCHAR(20),
    `gender` VARCHAR(10),
    `fullAddress` VARCHAR(200),
    `email` VARCHAR(50),
    `datetimeApplied` DATETIME NOT NULL,
    `applicationStatus` VARCHAR(20) NOT NULL,
    `handphoneNumber` VARCHAR(20),
    `guardianName` VARCHAR(80),
    `guardianNumber` VARCHAR(20),
    `healthIssue` VARCHAR(50),
    `identificationFrontPath` VARCHAR(100),
    `identificationBackPath` VARCHAR(100),
    `accountID` INT NOT NULL,
    PRIMARY KEY(`applicationID`),
  INDEX `fk_accountID` (`accountID`) USING BTREE,
	CONSTRAINT `fk_accountID` FOREIGN KEY (`accountID`) REFERENCES `Account` (`accountID`) ON UPDATE RESTRICT ON DELETE CASCADE
)
COLLATE='latin1_swedish_ci'
ENGINE=InnoDB
;

CREATE TABLE `PreUniQualification`(
    `preUniQualificationID` VARCHAR(10) NOT NULL,
    `qualificationName` VARCHAR(50) NOT NULL,
    `qualificationYear` VARCHAR(50),
    `docPath` VARCHAR(100) NOT NULL,
    `applicationID` int NOT NULL,
    PRIMARY KEY(`preUniQualificationID`),
    INDEX `fk_applicationID` (`applicationID`) USING BTREE,
	CONSTRAINT `fk_applicationID` FOREIGN KEY (`applicationID`) REFERENCES `Applications` (`applicationID`) ON UPDATE RESTRICT ON DELETE CASCADE
)
COLLATE='latin1_swedish_ci'
ENGINE=InnoDB
;

CREATE TABLE `PreUniSubject`(
    `preUniSubjectID` VARCHAR(10) NOT NULL,
    `subjectName` VARCHAR(50) NOT NULL,
    `subjectGrade` VARCHAR(50),
    `subjectScore` NUMERIC(5,2),
    `subjectStandard` VARCHAR(50),
    `preUniQualificationID` VARCHAR(10) NOT NULL,
    PRIMARY KEY(`preUniSubjectID`),
    INDEX `fk_preUniQualificationID` (`preUniQualificationID`) USING BTREE,
	CONSTRAINT `fk_preUniQualificationID` FOREIGN KEY (`preUniQualificationID`) REFERENCES `PreUniQualification` (`preUniQualificationID`) ON UPDATE RESTRICT ON DELETE CASCADE
)
COLLATE='latin1_swedish_ci'
ENGINE=InnoDB
;

CREATE TABLE `TertiaryQualification`(
    `tertiaryQualificationID` VARCHAR(10) NOT NULL,
    `qualificationName` VARCHAR(50) NOT NULL,
    `institutionType` VARCHAR(50) NOT NULL,
    `institutionState` VARCHAR(50) NOT NULL,
    `institutionName` VARCHAR(50) NOT NULL,
    `levelOfStudy` VARCHAR(50),
    `nameOfStudy` VARCHAR(50) NOT NULL,
    `studyStatus` VARCHAR(50),
    `docPath` VARCHAR(100),
    `bkaCodeTitle` VARCHAR(50),
    `bkaCredit` INT,
    `bkaGrade` VARCHAR(10),
    `applicationID` int NOT NULL,
    PRIMARY KEY(`tertiaryQualificationID`),
    INDEX `fk_applicationID2` (`applicationID`) USING BTREE,
	CONSTRAINT `fk_applicationID2` FOREIGN KEY (`applicationID`) REFERENCES `Applications` (`applicationID`) ON UPDATE RESTRICT ON DELETE CASCADE
)
COLLATE='latin1_swedish_ci'
ENGINE=InnoDB
;

CREATE TABLE `EnglishQualification`(
    `englishQualificationID` VARCHAR(10) NOT NULL,
    `qualificationName` VARCHAR(50) NOT NULL,
    `band` VARCHAR(10),
    `score` NUMERIC(5,2),
    `testDate` DATETIME,
    `expiryDate` DATETIME,
    `docPath` VARCHAR(100),
    `applicationID` int NOT NULL,
    PRIMARY KEY(`englishQualificationID`),
    INDEX `fk_applicationID3` (`applicationID`) USING BTREE,
	CONSTRAINT `fk_applicationID3` FOREIGN KEY (`applicationID`) REFERENCES `Applications` (`applicationID`) ON UPDATE RESTRICT ON DELETE CASCADE
)
COLLATE='latin1_swedish_ci'
ENGINE=InnoDB
;

CREATE TABLE `ApplicationProgramme`(
    `apID` INT AUTO_INCREMENT NOT NULL,
    `applicationID` int NOT NULL,
    `programmeCampusID` VARCHAR(10),
    `status` VARCHAR(15),
    PRIMARY KEY(`apID`),
    INDEX `fk_applicationID4` (`applicationID`) USING BTREE,
    INDEX `fk_programmeCampusID2` (`programmeCampusID`) USING BTREE,
	CONSTRAINT `fk_applicationID4` FOREIGN KEY (`applicationID`) REFERENCES `Applications` (`applicationID`) ON UPDATE RESTRICT ON DELETE CASCADE,
		CONSTRAINT `fk_programmeCampusID2` FOREIGN KEY (`programmeCampusID`) REFERENCES `ProgrammeCampus` (`programmeCampusID`) ON UPDATE RESTRICT ON DELETE CASCADE
)
COLLATE='latin1_swedish_ci'
ENGINE=InnoDB
;


INSERT INTO `Intake` (`intakeID`, `intakeName`, `intakeYear`, `intakeMonth`) VALUES ('I000000001', '202311', 2023, 11);

INSERT INTO `Academician` (`academicianID`, `academicianName`, `academicianTitle`, `academicianEmail`, `designation`, `department`, `educationBackground`, `publication`, `researchArea`, `organizationMembership`, `academicianURL`) VALUES ('A000000001', 'Choy Lai Fun', 'Pua', 'choylf@tarc.edu.my', 'Senior Lecturer', 'Faculty of Computing And Information Technology', 'AdvDipSc (TARC), BS (Campbell), MInfComnTechMgt (AeU)', NULL, 'ICT management, e-commerce, Computer systems architecture', NULL, './static/media/ChoyLaiFun.jpg');
INSERT INTO `Academician` (`academicianID`, `academicianName`, `academicianTitle`, `academicianEmail`, `designation`, `department`, `educationBackground`, `publication`, `researchArea`, `organizationMembership`, `academicianURL`) VALUES ('A000000002', 'Mazlinda Binti Nezam Mudeen', 'Cik', 'mazlindanm@tarc.edu.my', 'Lecturer', 'Department of Software Engineering And Technology Faculty of Computing And Information Technology', 'DipIT, BIT (Hons) (KLIUC), MSoftEng (UTM)', NULL, 'Software Engineering', NULL, './static/media/MazlindaBintiNezamMudeen.jpg');
INSERT INTO `Academician` (`academicianID`, `academicianName`, `academicianTitle`, `academicianEmail`, `designation`, `department`, `educationBackground`, `publication`, `researchArea`, `organizationMembership`, `academicianURL`) VALUES ('A000000003', 'Chee Keh Niang', 'Encik', 'cheekn@tarc.edu.my', 'Principal Lecturer', 'Department of Mathematical And Data Science Faculty of Computing And Information Technology', 'BSc (Hons), MSc (UPM)', NULL, 'Applied Statistics', NULL, './static/media/CheeKehNiang.jpg');
INSERT INTO `Academician` (`academicianID`, `academicianName`, `academicianTitle`, `academicianEmail`, `designation`, `department`, `educationBackground`, `publication`, `researchArea`, `organizationMembership`, `academicianURL`) VALUES ('A000000004', 'See Kwee Teck', 'Dr', 'seekt@tarc.edu.my', 'Assistant Professor', 'Department of Information Systems And Security Faculty of Computing And Information Technology', 'AdvDipSc (TARC), BS (Campbell), MSc (Liv.J.Moores), PhD (MMU)', NULL, 'Business information systems, multimedia systems, mobile assisted learning', NULL, './static/media/SeeKweeTeck.jpg');
INSERT INTO `Academician` (`academicianID`, `academicianName`, `academicianTitle`, `academicianEmail`, `designation`, `department`, `educationBackground`, `publication`, `researchArea`, `organizationMembership`, `academicianURL`) VALUES ('A000000005', 'Ho Chuk Fong', 'Dr', 'cfho@tarc.edu.my', 'Assistant Professor', 'Department of Software Engineering And Technology, Faculty of Computing And Information Technology', 'BCompSc (Hons), PhD (UPM)', NULL, 'Software Engineering', NULL, './static/media/HoChukFong.jpg');

INSERT INTO `Programme` (`programmeID`, `programmeName`, `programmeDescription`, `programmeDuration`,`programmeType`) VALUES ('FIC', 'Foundation in Computing', 'This program equips students with the foundational understanding needed for further academic or professional pursuits in the world of computing.',1, 'xDegree');
INSERT INTO `Programme` (`programmeID`, `programmeName`, `programmeDescription`, `programmeDuration`,`programmeType`) VALUES ('DIS', 'Diploma in Information Systems', 'This diploma focuses on the design and management of information systems, including database management, system analysis, and business processes.',2, 'xDegree');
INSERT INTO `Programme` (`programmeID`, `programmeName`, `programmeDescription`, `programmeDuration`,`programmeType`) VALUES ('DSS', 'Diploma in Information Technology', 'This program combines technical skills with IT management concepts, preparing students for roles in IT support, networking, and systems administration.',2, 'xDegree');
INSERT INTO `Programme` (`programmeID`, `programmeName`, `programmeDescription`, `programmeDuration`,`programmeType`) VALUES ('DSE', 'Diploma in Software Engineering', 'This diploma program emphasizes software development methodologies and coding skills to train students to create robust and efficient software applications.',2, 'xDegree');
INSERT INTO `Programme` (`programmeID`, `programmeName`, `programmeDescription`, `programmeDuration`,`programmeType`) VALUES ('BST', 'Bachelor of Computer Science in Interactive Software Technology', 'This degree program focuses on developing interactive and user-friendly software applications, including mobile apps and web development.',3, 'Degree');
INSERT INTO `Programme` (`programmeID`, `programmeName`, `programmeDescription`, `programmeDuration`,`programmeType`) VALUES ('BDS', 'Bachelor of Computer Science in Data Science', 'This program equips students with the skills needed to analyze and interpret data, making data-driven decisions and predictions using advanced techniques.',3, 'Degree');
INSERT INTO `Programme` (`programmeID`, `programmeName`, `programmeDescription`, `programmeDuration`,`programmeType`) VALUES ('BEI', 'Bachelor of Information Systems in Enterprise Information Systems', 'This degree concentrates on designing and managing information systems for large enterprises, emphasizing business process integration and efficiency.',3, 'Degree');
INSERT INTO `Programme` (`programmeID`, `programmeName`, `programmeDescription`, `programmeDuration`,`programmeType`) VALUES ('BIS', 'Bachelor of Information Technology in Information Security', 'This program trains students in cybersecurity, including threat detection, network security, and data protection, to safeguard digital assets.',3, 'Degree');

INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3162', 'Introduction to Information Technology', 'An introductory course covering the basics of information technology, including hardware, software, and their applications.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3163', 'Algebra', 'A foundational mathematics course focused on algebraic equations, operations, and concepts.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3164', 'Calculus and Algebra', 'A combination of calculus, which deals with rates of change and integration, and algebra, emphasizing equations and functions.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3165', 'Computer Systems Architecture', 'Exploring the design and components of computer systems, including CPUs, memory, and storage.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3166', 'Database Development and Applications', 'Learning about database design, development, and how databases are used in various applications.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3167', 'Discrete Mathematics', 'A mathematical course that deals with countable and distinct objects, often used in computer science and logic.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3168', 'Electronic Commerce', 'Studying the principles of conducting business transactions online and e-commerce strategies.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3169', 'Enterprise Resource Planning', 'Understanding how integrated software systems help manage business processes and resources.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3170', 'Fundamentals of Computer Networks', 'Learning the basics of computer networks, including protocols, topology, and network management.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3171', 'GUI and Web Application Programming', 'Exploring graphical user interface (GUI) and web application development using programming languages.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3172', 'Industrial Training', 'Practical training in an industrial or workplace setting, often as part of a cooperative education program.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3173', 'Introduction to Cybersecurity', 'An introduction to the principles and practices of cybersecurity, including threat detection and prevention.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3174', 'Introduction to Data Structures and Algorithms', 'Covering the fundamental data structures and algorithms used in programming.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3176', 'Introductory Calculus', 'An introductory course in calculus, focusing on differentiation and integration.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3177', 'Introductory Statistics', 'Basic concepts of statistics, including data analysis and interpretation.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3178', 'Managing Information Systems', 'Learning how to effectively manage information systems within organizations.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3179', 'Mini Project', 'A smaller-scale project designed to apply and demonstrate knowledge and skills acquired in coursework.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3180', 'Mobile Application Development', 'Developing applications for mobile devices, often using specific platforms or programming languages.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3181', 'Object-Oriented Programming Techniques', 'Understanding and applying object-oriented programming principles in software development.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3182', 'Operating Systems', 'Studying the design and operation of computer operating systems.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3183', 'Pre-Calculus', 'Building foundational mathematical concepts and skills necessary for advanced calculus.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3184', 'Principles of Accounting', 'An introduction to basic accounting principles and practices.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3185', 'Principles of Information Systems', 'Understanding the fundamental concepts and components of information systems.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3186', 'Probability and Statistics', 'A more advanced course covering probability theory and statistical analysis.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3187', 'Problem Solving and Programming', 'Developing problem-solving skills and basic programming techniques.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3188', 'Programming Concepts and Design I', 'An introductory course focusing on programming concepts and design.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3189', 'Programming Concepts and Design II', 'A continuation of programming concepts with more advanced topics.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3190', 'Software Engineering', 'Exploring the principles and practices of software development.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3191', 'Software Maintenance', 'Learning how to update and maintain existing software systems.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3192', 'Software Requirement and Design', 'Covering the process of gathering software requirements and designing software solutions.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3193', 'Software Testing and Quality', 'Understanding software testing methods and ensuring software quality.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3194', 'Statistics I', 'Advanced statistics covering various statistical techniques.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3195', 'Statistics II', 'Further advanced statistical analysis and techniques.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3196', 'Systems Analysis and Design', 'Learning how to analyze and design computer systems to meet specific requirements.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3197', 'Web Design and Development', 'Creating and designing websites for various purposes.');
INSERT INTO `Course` (`courseCode`, `courseName`, `courseDescription`) VALUES ('AACS3198', 'Web Systems and Technologies', 'Exploring web-related technologies and systems used in web development.');

INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000001',4, 'AACS3162', 'DIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000002',4, 'AACS3163', 'DIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000003',4, 'AACS3164', 'DIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000004',4, 'AACS3165', 'DIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000005',4, 'AACS3166', 'DIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000006',4, 'AACS3167', 'DIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000007',4, 'AACS3168', 'DIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000008',4, 'AACS3169', 'DIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000009',4, 'AACS3170', 'DIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000010',4, 'AACS3171', 'DIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000011',4, 'AACS3172', 'DIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000012',4, 'AACS3173', 'DIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000013',4, 'AACS3188', 'DIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000014',4, 'AACS3189', 'DIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000015',4, 'AACS3190', 'DIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000016',4, 'AACS3191', 'DIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000017',4, 'AACS3181', 'DIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000018',4, 'AACS3169', 'DSS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000019',4, 'AACS3170', 'DSS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000020',4, 'AACS3171', 'DSS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000021',4, 'AACS3172', 'DSS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000022',4, 'AACS3173', 'DSS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000023',4, 'AACS3174', 'DSS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000024',4, 'AACS3176', 'DSS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000025',4, 'AACS3177', 'DSS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000026',4, 'AACS3178', 'DSS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000027',4, 'AACS3179', 'DSS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000028',4, 'AACS3180', 'DSS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000029',4, 'AACS3181', 'DSS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000030',4, 'AACS3182', 'DSS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000031',4, 'AACS3183', 'DSS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000032',4, 'AACS3184', 'DSS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000033',4, 'AACS3185', 'DSS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000034',4, 'AACS3198', 'DSS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000035',4, 'AACS3184', 'DSE');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000036',4, 'AACS3185', 'DSE');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000037',4, 'AACS3186', 'DSE');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000038',4, 'AACS3187', 'DSE');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000039',4, 'AACS3188', 'DSE');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000040',4, 'AACS3189', 'DSE');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000041',4, 'AACS3190', 'DSE');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000042',4, 'AACS3191', 'DSE');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000043',4, 'AACS3192', 'DSE');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000044',4, 'AACS3193', 'DSE');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000045',4, 'AACS3194', 'DSE');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000046',4, 'AACS3195', 'DSE');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000047',4, 'AACS3196', 'DSE');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000048',4, 'AACS3197', 'DSE');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000049',4, 'AACS3198', 'DSE');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000050',4, 'AACS3162', 'DSE');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000051',4, 'AACS3163', 'DSE');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000052',4, 'AACS3166', 'FIC');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000053',4, 'AACS3167', 'FIC');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000054',4, 'AACS3168', 'FIC');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000055',4, 'AACS3169', 'FIC');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000056',4, 'AACS3170', 'FIC');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000057',4, 'AACS3171', 'FIC');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000058',4, 'AACS3172', 'FIC');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000059',4, 'AACS3173', 'FIC');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000060',4, 'AACS3174', 'FIC');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000061',4, 'AACS3176', 'FIC');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000062',4, 'AACS3177', 'FIC');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000063',4, 'AACS3178', 'FIC');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000064',4, 'AACS3179', 'FIC');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000065',4, 'AACS3180', 'FIC');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000066',4, 'AACS3181', 'FIC');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000067',4, 'AACS3182', 'FIC');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000068',4, 'AACS3183', 'FIC');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000069',4, 'AACS3167', 'BST');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000070',4, 'AACS3168', 'BST');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000071',4, 'AACS3169', 'BST');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000072',4, 'AACS3170', 'BST');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000073',4, 'AACS3171', 'BST');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000074',4, 'AACS3172', 'BST');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000075',4, 'AACS3173', 'BST');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000076',4, 'AACS3181', 'BST');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000077',4, 'AACS3182', 'BST');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000078',4, 'AACS3183', 'BST');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000079',4, 'AACS3184', 'BST');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000080',4, 'AACS3185', 'BST');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000081',4, 'AACS3186', 'BST');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000082',4, 'AACS3192', 'BST');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000083',4, 'AACS3193', 'BST');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000084',4, 'AACS3194', 'BST');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000085',4, 'AACS3195', 'BST');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000086',4, 'AACS3162', 'BDS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000087',4, 'AACS3163', 'BDS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000088',4, 'AACS3164', 'BDS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000089',4, 'AACS3165', 'BDS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000090',4, 'AACS3166', 'BDS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000091',4, 'AACS3167', 'BDS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000092',4, 'AACS3168', 'BDS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000093',4, 'AACS3169', 'BDS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000094',4, 'AACS3170', 'BDS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000095',4, 'AACS3171', 'BDS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000096',4, 'AACS3172', 'BDS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000097',4, 'AACS3173', 'BDS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000098',4, 'AACS3174', 'BDS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000099',4, 'AACS3176', 'BDS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000100',4, 'AACS3177', 'BDS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000101',4, 'AACS3178', 'BDS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000102',4, 'AACS3179', 'BDS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000103',4, 'AACS3181', 'BEI');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000104',4, 'AACS3182', 'BEI');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000105',4, 'AACS3183', 'BEI');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000106',4, 'AACS3184', 'BEI');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000107',4, 'AACS3185', 'BEI');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000108',4, 'AACS3186', 'BEI');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000109',4, 'AACS3187', 'BEI');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000110',4, 'AACS3188', 'BEI');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000111',4, 'AACS3189', 'BEI');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000112',4, 'AACS3190', 'BEI');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000113',4, 'AACS3191', 'BEI');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000114',4, 'AACS3192', 'BEI');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000115',4, 'AACS3193', 'BEI');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000116',4, 'AACS3194', 'BEI');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000117',4, 'AACS3195', 'BEI');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000118',4, 'AACS3196', 'BEI');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000119',4, 'AACS3197', 'BEI');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000120',4, 'AACS3173', 'BIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000121',4, 'AACS3174', 'BIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000122',4, 'AACS3176', 'BIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000123',4, 'AACS3177', 'BIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000124',4, 'AACS3178', 'BIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000125',4, 'AACS3179', 'BIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000126',4, 'AACS3180', 'BIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000127',4, 'AACS3181', 'BIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000128',4, 'AACS3182', 'BIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000129',4, 'AACS3183', 'BIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000130',4, 'AACS3184', 'BIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000131',4, 'AACS3185', 'BIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000132',4, 'AACS3186', 'BIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000133',4, 'AACS3187', 'BIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000134',4, 'AACS3188', 'BIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000135',4, 'AACS3189', 'BIS');
INSERT INTO `ProgrammeCourse` (`programmeCourseID`, `creditHour`, `courseCode`, `programmeID`) VALUES ('PC00000000000000000000136',4, 'AACS3190', 'BIS');

INSERT INTO `Campus` (`campusID`, `campusName`, `campusLocation`, `campusURL`) VALUES ('C000000001', 'KUALA LUMPUR CAMPUS', 'Jalan Genting Kelang, Setapak, 53300 Kuala Lumpur.', './static/media/klmain.jpg');
INSERT INTO `Campus` (`campusID`, `campusName`, `campusLocation`, `campusURL`) VALUES ('C000000002', 'PENANG BRANCH', '77, Lorong Lembah Permai Tiga, 11200 Tanjong Bungah, Pulau Pinang, Malaysia.', './static/media/penang.jpg');

INSERT INTO `ProgrammeCampus` (`programmeCampusID`, `startDate`, `programmeID`, `campusID`, `intakeID`) VALUES ('ProgC00001', '2023-02-11 00:00:00', 'BDS', 'C000000001', 'I000000001');
INSERT INTO `ProgrammeCampus` (`programmeCampusID`, `startDate`, `programmeID`, `campusID`, `intakeID`) VALUES ('ProgC00002', '2023-02-11 00:00:00', 'BDS', 'C000000002', 'I000000001');
INSERT INTO `ProgrammeCampus` (`programmeCampusID`, `startDate`, `programmeID`, `campusID`, `intakeID`) VALUES ('ProgC00003', '2023-02-11 00:00:00', 'BEI', 'C000000001', 'I000000001');
INSERT INTO `ProgrammeCampus` (`programmeCampusID`, `startDate`, `programmeID`, `campusID`, `intakeID`) VALUES ('ProgC00004', '2023-02-11 00:00:00', 'BIS', 'C000000001', 'I000000001');
INSERT INTO `ProgrammeCampus` (`programmeCampusID`, `startDate`, `programmeID`, `campusID`, `intakeID`) VALUES ('ProgC00005', '2023-02-11 00:00:00', 'BIS', 'C000000002', 'I000000001');
INSERT INTO `ProgrammeCampus` (`programmeCampusID`, `startDate`, `programmeID`, `campusID`, `intakeID`) VALUES ('ProgC00006', '2023-02-11 00:00:00', 'BST', 'C000000001', 'I000000001');
INSERT INTO `ProgrammeCampus` (`programmeCampusID`, `startDate`, `programmeID`, `campusID`, `intakeID`) VALUES ('ProgC00007', '2023-02-11 00:00:00', 'BST', 'C000000002', 'I000000001');
INSERT INTO `ProgrammeCampus` (`programmeCampusID`, `startDate`, `programmeID`, `campusID`, `intakeID`) VALUES ('ProgC00008', '2023-02-11 00:00:00', 'DIS', 'C000000001', 'I000000001');
INSERT INTO `ProgrammeCampus` (`programmeCampusID`, `startDate`, `programmeID`, `campusID`, `intakeID`) VALUES ('ProgC00009', '2023-02-11 00:00:00', 'DSE', 'C000000001', 'I000000001');
INSERT INTO `ProgrammeCampus` (`programmeCampusID`, `startDate`, `programmeID`, `campusID`, `intakeID`) VALUES ('ProgC00010', '2023-02-11 00:00:00', 'DSS', 'C000000001', 'I000000001');
INSERT INTO `ProgrammeCampus` (`programmeCampusID`, `startDate`, `programmeID`, `campusID`, `intakeID`) VALUES ('ProgC00011', '2023-02-11 00:00:00', 'DSS', 'C000000002', 'I000000001');
INSERT INTO `ProgrammeCampus` (`programmeCampusID`, `startDate`, `programmeID`, `campusID`, `intakeID`) VALUES ('ProgC00012', '2023-02-11 00:00:00', 'FIC', 'C000000001', 'I000000001');
INSERT INTO `ProgrammeCampus` (`programmeCampusID`, `startDate`, `programmeID`, `campusID`, `intakeID`) VALUES ('ProgC00013', '2023-02-11 00:00:00', 'FIC', 'C000000002', 'I000000001');

INSERT INTO `ProgrammeInCharge` (`programmeInChargeID`, `programmeCampusID`, `academicianID`) VALUES ('IC00000001', 'ProgC00001', 'A000000001');
INSERT INTO `ProgrammeInCharge` (`programmeInChargeID`, `programmeCampusID`, `academicianID`) VALUES ('IC00000002', 'ProgC00002', 'A000000001');
INSERT INTO `ProgrammeInCharge` (`programmeInChargeID`, `programmeCampusID`, `academicianID`) VALUES ('IC00000003', 'ProgC00003', 'A000000001');
INSERT INTO `ProgrammeInCharge` (`programmeInChargeID`, `programmeCampusID`, `academicianID`) VALUES ('IC00000004', 'ProgC00004', 'A000000002');
INSERT INTO `ProgrammeInCharge` (`programmeInChargeID`, `programmeCampusID`, `academicianID`) VALUES ('IC00000005', 'ProgC00005', 'A000000002');
INSERT INTO `ProgrammeInCharge` (`programmeInChargeID`, `programmeCampusID`, `academicianID`) VALUES ('IC00000006', 'ProgC00006', 'A000000003');
INSERT INTO `ProgrammeInCharge` (`programmeInChargeID`, `programmeCampusID`, `academicianID`) VALUES ('IC00000007', 'ProgC00007', 'A000000003');
INSERT INTO `ProgrammeInCharge` (`programmeInChargeID`, `programmeCampusID`, `academicianID`) VALUES ('IC00000008', 'ProgC00008', 'A000000003');
INSERT INTO `ProgrammeInCharge` (`programmeInChargeID`, `programmeCampusID`, `academicianID`) VALUES ('IC00000009', 'ProgC00009', 'A000000004');
INSERT INTO `ProgrammeInCharge` (`programmeInChargeID`, `programmeCampusID`, `academicianID`) VALUES ('IC00000010', 'ProgC00010', 'A000000004');
INSERT INTO `ProgrammeInCharge` (`programmeInChargeID`, `programmeCampusID`, `academicianID`) VALUES ('IC00000011', 'ProgC00011', 'A000000005');
INSERT INTO `ProgrammeInCharge` (`programmeInChargeID`, `programmeCampusID`, `academicianID`) VALUES ('IC00000012', 'ProgC00012', 'A000000005');
INSERT INTO `ProgrammeInCharge` (`programmeInChargeID`, `programmeCampusID`, `academicianID`) VALUES ('IC00000013', 'ProgC00013', 'A000000005');

INSERT INTO `QualificationSubject` (`qualificationSubjectID`, `subjectName`, `grade`, `qualificationName`, `programmeID`) VALUES('QS00000001', 'Additional Mathematics', 'C', 'SPM', 'DIS');
INSERT INTO `QualificationSubject` (`qualificationSubjectID`, `subjectName`, `grade`, `qualificationName`, `programmeID`) VALUES('QS00000002', 'Additional Mathematics', 'C', 'SPM', 'DSS');
INSERT INTO `QualificationSubject` (`qualificationSubjectID`, `subjectName`, `grade`, `qualificationName`, `programmeID`) VALUES('QS00000003', 'Mathematics', 'C', 'SPM', 'DSE');
INSERT INTO `QualificationSubject` (`qualificationSubjectID`, `subjectName`, `grade`, `qualificationName`, `programmeID`) VALUES('QS00000004', 'Mathematics', 'C', 'SPM', 'FIC');
INSERT INTO `QualificationSubject` (`qualificationSubjectID`, `subjectName`, `grade`, `qualificationName`, `programmeID`) VALUES('QS00000005', 'English', 'C', 'SPM', 'DIS');
INSERT INTO `QualificationSubject` (`qualificationSubjectID`, `subjectName`, `grade`, `qualificationName`, `programmeID`) VALUES('QS00000006', 'English', 'C', 'SPM', 'DSS');
INSERT INTO `QualificationSubject` (`qualificationSubjectID`, `subjectName`, `grade`, `qualificationName`, `programmeID`) VALUES('QS00000007', 'English', 'C', 'SPM', 'DSE');
INSERT INTO `QualificationSubject` (`qualificationSubjectID`, `subjectName`, `grade`, `qualificationName`, `programmeID`) VALUES('QS00000008', 'English', 'C', 'SPM', 'FIC');
INSERT INTO `QualificationSubject` (`qualificationSubjectID`, `subjectName`, `grade`, `qualificationName`, `programmeID`) VALUES('QS00000009', 'Diploma in Computer Science', NULL, 'Diploma', 'BST');
INSERT INTO `QualificationSubject` (`qualificationSubjectID`, `subjectName`, `grade`, `qualificationName`, `programmeID`) VALUES('QS00000010', 'Diploma in Computer Science', NULL, 'Diploma', 'BDS');
INSERT INTO `QualificationSubject` (`qualificationSubjectID`, `subjectName`, `grade`, `qualificationName`, `programmeID`) VALUES('QS00000011', 'Diploma in Computer Science', NULL, 'Diploma', 'BEI');
INSERT INTO `QualificationSubject` (`qualificationSubjectID`, `subjectName`, `grade`, `qualificationName`, `programmeID`) VALUES('QS00000012', 'Diploma in Computer Science', NULL, 'Diploma', 'BIS');
INSERT INTO `QualificationSubject` (`qualificationSubjectID`, `subjectName`, `grade`, `qualificationName`, `programmeID`) VALUES('QS00000013', 'Diploma in Information Systems', NULL, 'Diploma', 'BDS');
INSERT INTO `QualificationSubject` (`qualificationSubjectID`, `subjectName`, `grade`, `qualificationName`, `programmeID`) VALUES('QS00000014', 'Diploma in Information Systems', NULL, 'Diploma', 'BEI');
INSERT INTO `QualificationSubject` (`qualificationSubjectID`, `subjectName`, `grade`, `qualificationName`, `programmeID`) VALUES('QS00000015', 'Diploma in Information Systems', NULL, 'Diploma', 'BIS');
INSERT INTO `QualificationSubject` (`qualificationSubjectID`, `subjectName`, `grade`, `qualificationName`, `programmeID`) VALUES('QS00000016', 'Diploma in Information Technology', NULL, 'Diploma', 'BST');
INSERT INTO `QualificationSubject` (`qualificationSubjectID`, `subjectName`, `grade`, `qualificationName`, `programmeID`) VALUES('QS00000017', 'Diploma in Information Technology', NULL, 'Diploma', 'BDS');
INSERT INTO `QualificationSubject` (`qualificationSubjectID`, `subjectName`, `grade`, `qualificationName`, `programmeID`) VALUES('QS00000018', 'Diploma in Software Engineering', NULL, 'Diploma', 'BIS');
INSERT INTO `QualificationSubject` (`qualificationSubjectID`, `subjectName`, `grade`, `qualificationName`, `programmeID`) VALUES('QS00000019', 'Diploma in Software Engineering', NULL, 'Diploma', 'BEI');