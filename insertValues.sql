-- pw jsmith123
insert into user values ('james.smith', '7cf2e5f72d3e144cad58f95214f2dd20ad8f9979f34d561433a31dacbc16071b', 'James', 'Smith', 'Approved');
-- pw msmith456
insert into user values ('michael.smith', '6d3a26d88ea77a9b07d79a48307644cd88976173f49f279fed04b681d713a541', 'Michael', 'Smith', 'Approved');
-- pw rsmith789
insert into user values ('robert.smith', '232c98d6f01474e874341b78d28064ac6c318763dbf80b057e0ea116905c7fcc', 'Robert', 'Smith', 'Approved');
-- pw mgarcia123
insert into user values ('maria.garcia', 'ddbdea14aecce91cd12172bce09e9b402a29ea0c2813dc35935095ead340cc35', 'Maria', 'Garcia', 'Approved');
-- pw dsmith456
insert into user values ('david.smith', 'f79704e124b997b32bd83c014b05c20413c6a3e928ec8083bf1872c82c025672', 'David', 'Smith', 'Approved');
-- pw manager1
insert into user values ('manager1', '380f9771d2df8566ce2bd5b8ed772b0bb74fd6457fb803ab2d267c394d89c750', 'Manager', 'One', 'Pending');
-- pw manager2
insert into user values ('manager2', '9d05b6092d975b0884c6ba7fadb283ced03da9822ebbd13cc6b6d1855a6495ec', 'Manager', 'Two', 'Approved');
-- pw manager3
insert into user values ('manager3', '42385b24804a6609a2744d414e0bf945704427b256ab79144b9ba93f278dbea7', 'Manager', 'Three', 'Approved');
-- pw manager4
insert into user values ('manager4', 'e3c0f6e574f2e758a4d9d271fea62894230126062d74fd6d474e2046837f9bce', 'Manager', 'Four', 'Approved');
-- pw manager5
insert into user values ('manager5', '60c6fc387428b43201be7da60da59934acb080b254e4eebead657b54154fbeb1', 'Manager', 'Five', 'Approved');
-- pw mrodriguez
insert into user values ('maria.rodriguez', 'c50218388d572cbe6aac09b33ceb5189608d5b9ede429b5a17562a17fdd547c4', 'Maria', 'Rodriguez', 'Declined');
-- pw msmith789
insert into user values ('mary.smith', '9ddbd60268ae6987437511066a2000f1f0017c23728700f9794628a9d3d33034', 'Mary', 'Smith', 'Approved');
-- pw mhernandez
insert into user values ('maria.hernandez', '600d2690306308866676b4229d51e04857876021705362bf3b26b08a1f78f9cb', 'Maria', 'Hernandez', 'Approved');
-- pw staff1234
insert into user values ('staff1', '02defbfb8190f9d0719ef7a23da2049bd2e61442bc14021a6d8a4ae35ca334b7', 'Staff', 'One', 'Approved');
-- pw staff4567
insert into user values ('staff2', '6bd0987c664d5e7551004d30656ae1d12b9d262e2d128ba4200934b4116d96cd', 'Staff', 'Two', 'Approved');
-- pw staff7890
insert into user values ('staff3', '8857a879cbea64f2d20c6c1bfab505f4b23c06d28decb3b9ddc5426b75f469f1', 'Staff', 'Three', 'Approved');
-- pw user123456
insert into user values ('user1', '90aae915da86d3b3a4da7a996bc264bfbaf50a953cbbe8cd3478a2a6ccc7b900', 'User', 'One', 'Pending');
-- pw visitor123
insert into user values ('visitor1', '5c1e1b5c8936669bfe844210fb7ae7d3411dd9f41614d09ce9732dfc17c266bc', 'Visitor', 'One', 'Approved');


insert into visitor values ('michael.smith');
insert into visitor values ('maria.garcia');
insert into visitor values ('manager2');
insert into visitor values ('manager4');
insert into visitor values ('manager5');
insert into visitor values ('maria.rodriguez');
insert into visitor values ('mary.smith');
insert into visitor values ('staff2');
insert into visitor values ('staff3');
insert into visitor values ('visitor1');

insert into emails values ('james.smith', 'jsmith@gmail.com');
insert into emails values ('james.smith', 'jsmith@hotmail.com');
insert into emails values ('james.smith', 'jsmith@gatech.edu');
insert into emails values ('james.smith', 'jsmith@outlook.com');
insert into emails values ('michael.smith', 'msmith@gmail.com');
insert into emails values ('robert.smith', 'rsmith@hotmail.com');
insert into emails values ('maria.garcia', 'mgarcia@yahoo.com');
insert into emails values ('maria.garcia', 'mgarcia@gatech.edu');
insert into emails values ('david.smith', 'dsmith@outlook.com');
insert into emails values ('maria.rodriguez', 'mrodriguez@gmail.com');
insert into emails values ('mary.smith', 'mary@outlook.com');
insert into emails values ('maria.hernandez', 'mh@gatech.edu');
insert into emails values ('maria.hernandez', 'mh123@gmail.com');
insert into emails values ('manager1', 'm1@beltline.com');
insert into emails values ('manager2', 'm2@beltline.com');
insert into emails values ('manager3', 'm3@beltline.com');
insert into emails values ('manager4', 'm4@beltline.com');
insert into emails values ('manager5', 'm5@beltline.com');
insert into emails values ('staff1', 's1@beltline.com');
insert into emails values ('staff2', 's2@beltline.com');
insert into emails values ('staff3', 's3@beltline.com');
insert into emails values ('user1', 'u1@beltline.com');
insert into emails values ('visitor1', 'v1@beltline.com');

insert into employee values ('james.smith', 000000001, '4043721234', '123 East Main Street', 'Rochester', 'NY', '14604');
insert into employee values ('michael.smith', 000000002, '4043726789', '350 Ferst Drive', 'Atlanta', 'GA', '30332');
insert into employee values ('robert.smith', 000000003, '1234567890', '123 East Main Street', 'Columbus', 'OH', '43215');
insert into employee values ('maria.garcia', 000000004, '7890123456', '123 East Main Street', 'Richland', 'PA', '17987');
insert into employee values ('david.smith', 000000005, '5124776435', '350 Ferst Drive', 'Atlanta', 'GA', '30332');
insert into employee values ('manager1', 000000006, '8045126767', '123 East Main Street', 'Rochester', 'NY', '14604');
insert into employee values ('manager2', 000000007, '9876543210', '123 East Main Street', 'Rochester', 'NY', '14604');
insert into employee values ('manager3', 000000008, '5432167890', '350 Ferst Drive', 'Atlanta', 'GA', '30332');
insert into employee values ('manager4', 000000009, '8053467565', '123 East Main Street', 'Columbus', 'OH', '43215');
insert into employee values ('manager5', 000000010, '8031446782', '801 Atlantic Drive', 'Atlanta', 'GA', '30332');
insert into employee values ('staff1', 000000011, '8024456765', '266 Ferst Drive Northwest', 'Atlanta', 'GA', '30332');
insert into employee values ('staff2', 000000012, '8888888888', '266 Ferst Drive Northwest', 'Atlanta', 'GA', '30332');
insert into employee values ('staff3', 000000013, '3333333333', '801 Atlantic Drive', 'Atlanta', 'GA', '30332');

insert into administrator values ('james.smith');

insert into staff values ('michael.smith');
insert into staff values ('robert.smith');
insert into staff values ('staff1');
insert into staff values ('staff2');
insert into staff values ('staff3');

insert into manager values ('maria.garcia');
insert into manager values ('david.smith');
insert into manager values ('manager1');
insert into manager values ('manager2');
insert into manager values ('manager3');
insert into manager values ('manager4');
insert into manager values ('manager5');

insert into site values ('Piedmont Park', '400 Park Drive Northeast', '30306', true, 'manager2');
insert into site values ('Atlanta Beltline Center', '112 Krog Street Northeast', '30307', false, 'manager3');
insert into site values ('Historic Fourth Ward Park', '680 Dallas Street Northeast', '30308', true, 'manager4');
insert into site values ('Westview Cemetery', '1680 Westview Drive Southwest', '30310', false, 'manager5');
insert into site values ('Inman Park', '', '30307', true, 'david.smith');

insert into event values ('Piedmont Park', 'Eastside Trail', '2019-02-04', '2019-02-05', 0, 99999, 1, 'A combination of multi-use trail and linear green space, the Eastside Trail was the first finished section of the Atlanta BeltLine trail in the old rail corridor. The Eastside Trail, which was funded by a combination of public and private philanthropic sources, runs from the tip of Piedmont Park to Reynoldstown. More details at https://beltline.org/explore-atlanta-beltline-trails/eastside-trail/');
insert into event values ('Inman Park', 'Eastside Trail', '2019-02-04', '2019-02-05', 0, 99999, 1, 'A combination of multi-use trail and linear green space, the Eastside Trail was the first finished section of the Atlanta BeltLine trail in the old rail corridor. The Eastside Trail, which was funded by a combination of public and private philanthropic sources, runs from the tip of Piedmont Park to Reynoldstown. More details at https://beltline.org/explore-atlanta-beltline-trails/eastside-trail/');
insert into event values ('Inman Park', 'Eastside Trail', '2019-03-01', '2019-03-02', 0, 99999, 1, 'A combination of multi-use trail and linear green space, the Eastside Trail was the first finished section of the Atlanta BeltLine trail in the old rail corridor. The Eastside Trail, which was funded by a combination of public and private philanthropic sources, runs from the tip of Piedmont Park to Reynoldstown. More details at https://beltline.org/explore-atlanta-beltline-trails/eastside-trail/');
insert into event values ('Historic Fourth Ward Park', 'Eastside Trail', '2019-02-13', '2019-02-14', 0, 99999, 1, 'A combination of multi-use trail and linear green space, the Eastside Trail was the first finished section of the Atlanta BeltLine trail in the old rail corridor. The Eastside Trail, which was funded by a combination of public and private philanthropic sources, runs from the tip of Piedmont Park to Reynoldstown. More details at https://beltline.org/explore-atlanta-beltline-trails/eastside-trail/');
insert into event values ('Westview Cemetery', 'Westside Trail', '2019-02-18', '2019-02-21', 0, 99999, 1, 'The Westside Trail is a free amenity that offers a bicycle and pedestrian-safe corridor with a 14-foot-wide multi-use trail surrounded by mature trees and grasses thanks to Trees Atlanta’s Arboretum. With 16 points of entry, 14 of which will be ADA-accessible with ramp and stair systems, the trail provides numerous access points for people of all abilities. More details at: https://beltline.org/explore-atlanta-beltline-trails/westside-trail/');
insert into event values ('Inman Park', 'Bus Tour', '2019-02-01', '2019-02-02', 25, 6, 2, 'The Atlanta BeltLine Partnership’s tour program operates with a natural gas-powered, ADA accessible tour bus funded through contributions from 10th & Monroe, LLC, SunTrust Bank Trusteed Foundations–Florence C. and Harry L. English Memorial Fund and Thomas Guy Woolford Charitable Trust, and AGL Resources');
insert into event values ('Inman Park', 'Bus Tour', '2019-02-08', '2019-02-10', 25, 6, 2, 'The Atlanta BeltLine Partnership’s tour program operates with a natural gas-powered, ADA accessible tour bus funded through contributions from 10th & Monroe, LLC, SunTrust Bank Trusteed Foundations–Florence C. and Harry L. English Memorial Fund and Thomas Guy Woolford Charitable Trust, and AGL Resources');
insert into event values ('Inman Park', 'Private Bus Tour', '2019-02-01', '2019-02-02', 40, 4, 1, 'Private tours are available most days, pending bus and tour guide availability. Private tours can accommodate up to 4 guests per tour, and are subject to a tour fee (nonprofit rates are available). As a nonprofit organization with limited resources, we are unable to offer free private tours. We thank you for your support and your understanding as we try to provide as many private group tours as possible. The Atlanta BeltLine Partnership’s tour program operates with a natural gas-powered, ADA accessible tour bus funded through contributions from 10th & Monroe, LLC, SunTrust Bank Trusteed Foundations–Florence C. and Harry L. English Memorial Fund and Thomas Guy Woolford Charitable Trust, and AGL Resources');
insert into event values ('Inman Park', 'Arboretum Walking Tour', '2019-02-08', '2019-02-11', 5, 5, 1, 'Official Atlanta BeltLine Arboretum Walking Tours provide an up-close view of the Westside Trail and the Atlanta BeltLine Arboretum led by Trees Atlanta Docents. The one and a half hour tours step off at at 10am (Oct thru May), and 9am (June thru September). Departure for all tours is from Rose Circle Park near Brown Middle School. More details at: https://beltline.org/visit/atlanta-beltline-tours/#arboretum-walking');
insert into event values ('Atlanta Beltline Center', 'Official Atlanta BeltLine Bike Tour', '2019-02-09', '2019-02-14', 5, 5, 1, 'These tours will include rest stops highlighting assets and points of interest along the Atlanta BeltLine. Staff will lead the rides, and each group will have a ride sweep to help with any unexpected mechanical difficulties.');

insert into transit values ('MARTA', 'Blue', 2.00);
insert into transit values ('Bus', '152', 2.00);
insert into transit values ('Bike', 'Relay', 1.00);

insert into connect values ('Inman Park', 'MARTA', 'Blue');
insert into connect values ('Piedmont Park', 'MARTA', 'Blue');
insert into connect values ('Historic Fourth Ward Park', 'MARTA', 'Blue');
insert into connect values ('Westview Cemetery', 'MARTA', 'Blue');
insert into connect values ('Inman Park', 'Bus', '152');
insert into connect values ('Piedmont Park', 'Bus', '152');
insert into connect values ('Historic Fourth Ward Park', 'Bus', '152');
insert into connect values ('Piedmont Park', 'Bike', 'Relay');
insert into connect values ('Historic Fourth Ward Park', 'Bike', 'Relay');

insert into take values ('manager2', 'MARTA', 'Blue', '2019-03-20');
insert into take values ('manager2', 'Bus', '152', '2019-03-20');
insert into take values ('manager3', 'Bike', 'Relay', '2019-03-20');
insert into take values ('manager2', 'MARTA', 'Blue', '2019-03-21');
insert into take values ('maria.hernandez', 'Bus', '152', '2019-03-20');
insert into take values ('maria.hernandez', 'Bike', 'Relay', '2019-03-20');
insert into take values ('manager2', 'MARTA', 'Blue', '2019-03-22');
insert into take values ('maria.hernandez', 'Bus', '152', '2019-03-22');
insert into take values ('mary.smith', 'Bike', 'Relay', '2019-03-23');
insert into take values ('visitor1', 'MARTA', 'Blue', '2019-03-21');

insert into assignto values ('michael.smith', 'Piedmont Park', 'Eastside Trail', '2019-02-04');
insert into assignto values ('staff1', 'Piedmont Park', 'Eastside Trail', '2019-02-04');
insert into assignto values ('robert.smith', 'Inman Park', 'Eastside Trail', '2019-02-04');
insert into assignto values ('staff2', 'Inman Park', 'Eastside Trail', '2019-02-04');
insert into assignto values ('staff1', 'Inman Park', 'Eastside Trail', '2019-03-01');
insert into assignto values ('michael.smith', 'Historic Fourth Ward Park', 'Eastside Trail', '2019-02-13');
insert into assignto values ('staff1', 'Westview Cemetery', 'Westside Trail', '2019-02-18');
insert into assignto values ('staff3', 'Westview Cemetery', 'Westside Trail', '2019-02-18');
insert into assignto values ('michael.smith', 'Inman Park', 'Bus Tour', '2019-02-01');
insert into assignto values ('staff2', 'Inman Park', 'Bus Tour', '2019-02-01');
insert into assignto values ('robert.smith', 'Inman Park', 'Bus Tour', '2019-02-08');
insert into assignto values ('michael.smith', 'Inman Park', 'Bus Tour', '2019-02-08');
insert into assignto values ('robert.smith', 'Inman Park', 'Private Bus Tour', '2019-02-01');
insert into assignto values ('staff3', 'Inman Park', 'Arboretum Walking Tour', '2019-02-08');
insert into assignto values ('staff1', 'Atlanta BeltLine Center', 'Official Atlanta BeltLine Bike Tour', '2019-02-09');

insert into visitevent values ('mary.smith', 'Inman Park', 'Bus Tour', '2019-02-01', '2019-02-01');
insert into visitevent values ('maria.garcia', 'Inman Park', 'Bus Tour', '2019-02-01', '2019-02-02');
insert into visitevent values ('manager2', 'Inman Park', 'Bus Tour', '2019-02-01', '2019-02-02');
insert into visitevent values ('manager4', 'Inman Park', 'Bus Tour', '2019-02-01', '2019-02-01');
insert into visitevent values ('manager5', 'Inman Park', 'Bus Tour', '2019-02-01', '2019-02-02');
insert into visitevent values ('staff2', 'Inman Park', 'Bus Tour', '2019-02-01', '2019-02-02');
insert into visitevent values ('mary.smith', 'Westview Cemetery', 'Westside Trail', '2019-02-18', '2019-02-19');
insert into visitevent values ('mary.smith', 'Inman Park', 'Private Bus Tour', '2019-02-01', '2019-02-01');
insert into visitevent values ('mary.smith', 'Inman Park', 'Private Bus Tour', '2019-02-01', '2019-02-02');
insert into visitevent values ('mary.smith', 'Atlanta BeltLine Center', 'Official Atlanta BeltLine Bike Tour', '2019-02-09', '2019-02-10');
insert into visitevent values ('mary.smith', 'Inman Park', 'Arboretum Walking Tour', '2019-02-08', '2019-02-10');
insert into visitevent values ('mary.smith', 'Piedmont Park', 'Eastside Trail', '2019-02-04', '2019-02-04');
insert into visitevent values ('mary.smith', 'Historic Fourth Ward Park', 'Eastside Trail', '2019-02-13', '2019-02-13');
insert into visitevent values ('mary.smith', 'Historic Fourth Ward Park', 'Eastside Trail', '2019-02-13', '2019-02-14');
insert into visitevent values ('visitor1', 'Historic Fourth Ward Park', 'Eastside Trail', '2019-02-13', '2019-02-14');
insert into visitevent values ('visitor1', 'Atlanta BeltLine Center', 'Official Atlanta BeltLine Bike Tour', '2019-02-09', '2019-02-10');
insert into visitevent values ('visitor1', 'Westview Cemetery', 'Westside Trail', '2019-02-18', '2019-02-19');

insert into visitsite values ('mary.smith', 'Inman Park', '2019-02-01');
insert into visitsite values ('mary.smith', 'Inman Park', '2019-02-02');
insert into visitsite values ('mary.smith', 'Inman Park', '2019-02-03');
insert into visitsite values ('mary.smith', 'Atlanta BeltLine Center', '2019-02-01');
insert into visitsite values ('mary.smith', 'Atlanta BeltLine Center', '2019-02-10');
insert into visitsite values ('mary.smith', 'Historic Fourth Ward Park', '2019-02-02');
insert into visitsite values ('mary.smith', 'Piedmont Park', '2019-02-02');
insert into visitsite values ('visitor1', 'Piedmont Park', '2019-02-11');
insert into visitsite values ('visitor1', 'Atlanta BeltLine Center', '2019-02-13');
insert into visitsite values ('visitor1', 'Historic Fourth Ward Park', '2019-02-11');
insert into visitsite values ('visitor1', 'Westview Cemetery', '2019-02-06');
insert into visitsite values ('visitor1', 'Inman Park', '2019-02-01');
insert into visitsite values ('visitor1', 'Piedmont Park', '2019-02-01');
insert into visitsite values ('visitor1', 'Atlanta BeltLine Center', '2019-02-09');