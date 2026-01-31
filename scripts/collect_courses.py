"""
Course Data Collection Script

This script collects UBC course data from public sources:
1. UBC Academic Calendar (official course descriptions)
2. UBCGrades API (course listings and statistics)

Data Sources:
- https://vancouver.calendar.ubc.ca/course-descriptions/subject/cpscv
- https://ubcgrades.com/api/v3/courses/UBCV/{subject}

For this proof-of-concept, we use curated data from the UBC Academic Calendar
focused on Computer Science, Data Science, and Statistics courses -
the most relevant subjects for an AI Developer role application.
"""

import json
from pathlib import Path
from datetime import datetime

# Course data sourced from UBC Academic Calendar
# https://vancouver.calendar.ubc.ca/course-descriptions/subject/cpscv
# Last accessed: January 2026

COURSES = [
    # ============================================
    # COMPUTER SCIENCE - Foundational (100-200 level)
    # ============================================
    {
        "course_code": "CPSC 100",
        "title": "Computational Thinking",
        "description": "Meaning and impact of computational thinking. Solving problems using computational thinking, testing, debugging. No prior computing experience required.",
        "prerequisites": "None",
        "credits": 3,
        "department": "Computer Science",
        "level": "First Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 103",
        "title": "Introduction to Systematic Program Design",
        "description": "Computation as a tool for systematic problem solving in non-computer-science disciplines. Computational representation of information. The analysis of algorithms. Using abstraction to manage complexity.",
        "prerequisites": "None",
        "credits": 3,
        "department": "Computer Science",
        "level": "First Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 107",
        "title": "Systematic Program Design",
        "description": "Fundamental computation and program structures. Continuing systematic program design from CPSC 103.",
        "prerequisites": "CPSC 103",
        "credits": 3,
        "department": "Computer Science",
        "level": "First Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 110",
        "title": "Computation, Programs, and Programming",
        "description": "Fundamental program and computation structures. Introductory programming skills. Computation as a tool for information processing, simulation and modelling, and interacting with the world.",
        "prerequisites": "None",
        "credits": 4,
        "department": "Computer Science",
        "level": "First Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 121",
        "title": "Models of Computation",
        "description": "Physical and mathematical structures of computation. Boolean algebra and combinations logic circuits; proof techniques; functions and sequential circuits; sets and relations; finite state machines.",
        "prerequisites": "Principles of Mathematics 12 or Pre-calculus 12. Corequisite: CPSC 107 or CPSC 110",
        "credits": 4,
        "department": "Computer Science",
        "level": "First Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 203",
        "title": "Programming, Problem Solving, and Algorithms",
        "description": "Analysis of increasingly complex algorithmic problems, using a modern programming language and a variety of approaches. Implementing, testing, debugging programs. Creating and applying fundamental algorithms.",
        "prerequisites": "One of CPSC 103, CPSC 110, APSC 160, EOSC 211, MATH 210, or PHYS 210",
        "credits": 3,
        "department": "Computer Science",
        "level": "Second Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 210",
        "title": "Software Construction",
        "description": "Design, development, and analysis of robust software components. Topics such as software design, computational models, data structures, debugging, and testing.",
        "prerequisites": "One of CPSC 107 or CPSC 110",
        "credits": 4,
        "department": "Computer Science",
        "level": "Second Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 213",
        "title": "Introduction to Computer Systems",
        "description": "Software architecture, operating systems, and I/O architectures. Relationships between application software, operating systems, and computing hardware; critical sections, deadlock avoidance, and performance.",
        "prerequisites": "All of CPSC 121 and CPSC 210",
        "credits": 4,
        "department": "Computer Science",
        "level": "Second Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 221",
        "title": "Basic Algorithms and Data Structures",
        "description": "Design and analysis of basic algorithms and data structures; algorithm analysis methods, searching and sorting algorithms, basic data structures, graphs and concurrency.",
        "prerequisites": "One of CPSC 210 or CPEN 221; and one of CPSC 121, MATH 220, or 68% in MATH 226",
        "credits": 4,
        "department": "Computer Science",
        "level": "Second Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 259",
        "title": "Data Structures and Algorithms for Electrical Engineers",
        "description": "Advanced procedural programming. Fundamental algorithms for sorting and searching. Data structures including lists, trees, and hash tables. Introduction to algorithmic complexity.",
        "prerequisites": "APSC 160",
        "credits": 4,
        "department": "Computer Science",
        "level": "Second Year",
        "source": "UBC Academic Calendar"
    },

    # ============================================
    # COMPUTER SCIENCE - Intermediate (300 level)
    # ============================================
    {
        "course_code": "CPSC 302",
        "title": "Numerical Computation for Algebraic Problems",
        "description": "Numerical techniques for basic mathematical processes involving no discretization. Solution of linear systems, eigenvalue problems, nonlinear equations.",
        "prerequisites": "One of CPSC 103, 110, CPEN 221, EOSC 211, PHYS 210; and MATH 101; and one of MATH 152, 221, or 223",
        "credits": 3,
        "department": "Computer Science",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 303",
        "title": "Numerical Approximation and Discretization",
        "description": "Numerical techniques for basic mathematical processes involving discretization. Interpolation, approximation, numerical differentiation and integration, initial-value ordinary differential equations.",
        "prerequisites": "One of CPSC 103, 110, CPEN 221, EOSC 211, PHYS 210; and MATH 101; and one of MATH 152, 221, or 223",
        "credits": 3,
        "department": "Computer Science",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 304",
        "title": "Introduction to Relational Databases",
        "description": "Overview of database systems, ER models, logical database design and normalization, formal relational query languages, SQL and other commercial languages, transactions, concurrency control.",
        "prerequisites": "CPSC 221",
        "credits": 3,
        "department": "Computer Science",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 310",
        "title": "Introduction to Software Engineering",
        "description": "Specification, design, validation, evolution and construction of modern software systems within socially and professionally relevant domains.",
        "prerequisites": "All of CPSC 213 and CPSC 221",
        "credits": 4,
        "department": "Computer Science",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 311",
        "title": "Definition of Programming Languages",
        "description": "Comparative study of advanced programming language features. Statement types, data types, variable binding, parameter passing mechanisms. Methods for specifying the syntax and semantics of programming languages.",
        "prerequisites": "CPSC 210",
        "credits": 3,
        "department": "Computer Science",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 312",
        "title": "Functional and Logic Programming",
        "description": "Principles of symbolic computing, using languages based upon first-order logic and the lambda calculus. Recursion, search/backtracking, unification, lazy evaluation.",
        "prerequisites": "One of CPSC 210 or CPEN 221",
        "credits": 3,
        "department": "Computer Science",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 313",
        "title": "Computer Hardware and Operating Systems",
        "description": "Instruction sets, pipelining, code optimization, caching, virtual memory management, dynamically linked libraries, exception processing, concurrency.",
        "prerequisites": "CPSC 213 and CPSC 221",
        "credits": 3,
        "department": "Computer Science",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 314",
        "title": "Computer Graphics",
        "description": "Human vision and colour; geometric transformations; algorithms for 2-D and 3-D graphics; hardware and system architectures; shading and lighting; animation.",
        "prerequisites": "CPSC 221; and one of MATH 200, 217, 226, 253; and one of MATH 152, 221, 223",
        "credits": 3,
        "department": "Computer Science",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 317",
        "title": "Internet Computing",
        "description": "Computer networking, basic communication protocols, network infrastructure and routing. Application-level protocols and distributed applications.",
        "prerequisites": "CPSC 213 and CPSC 221",
        "credits": 3,
        "department": "Computer Science",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 319",
        "title": "Software Engineering Project",
        "description": "The design, implementation, and test of a large software system, using a team approach.",
        "prerequisites": "CPSC 310",
        "credits": 4,
        "department": "Computer Science",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 320",
        "title": "Intermediate Algorithm Design and Analysis",
        "description": "Systematic study of basic concepts and techniques in the design and analysis of algorithms, illustrated from various problem areas. Topics include: divide and conquer, greedy algorithms, dynamic programming, graph algorithms, NP-completeness.",
        "prerequisites": "CPSC 221; and at least 3 credits from COMM 291, BIOL 300, or MATH/STAT at 200+ level",
        "credits": 3,
        "department": "Computer Science",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 322",
        "title": "Introduction to Artificial Intelligence",
        "description": "Problem-solving and planning; state/action models and constraint satisfaction; search, game playing; knowledge representation and reasoning; natural language understanding; introduction to machine learning.",
        "prerequisites": "CPSC 221",
        "credits": 3,
        "department": "Computer Science",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 330",
        "title": "Applied Machine Learning",
        "description": "Application of machine learning tools, with an emphasis on solving practical problems. Data cleaning, feature extraction, supervised and unsupervised machine learning, reproducible workflows, and communicating results.",
        "prerequisites": "One of CPSC 203, CPSC 210, CPEN 221; or MATH 210 and one of CPSC 107, 110",
        "credits": 3,
        "department": "Computer Science",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 340",
        "title": "Machine Learning and Data Mining",
        "description": "Models of algorithms for dimensionality reduction, clustering, and pattern recognition. Emphasis on large datasets. Applications include classification, prediction, data visualization, recommender systems.",
        "prerequisites": "CPSC 221; and MATH 152/221/223; and MATH 200/217/226/253; and STAT 200/241/251 or equivalent",
        "credits": 3,
        "department": "Computer Science",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 344",
        "title": "Introduction to Human Computer Interaction Methods",
        "description": "Basic tools and techniques, teaching a systematic approach to interface design, task analysis, analytic and empirical evaluation methods.",
        "prerequisites": "One of CPSC 210 or CPEN 221",
        "credits": 3,
        "department": "Computer Science",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 368",
        "title": "Databases in Data Science",
        "description": "Overview of relational and non-relational database systems, role and usage when querying data, data modelling, query languages, optimization for analytics workloads.",
        "prerequisites": "One of CPSC 203, CPSC 210, CPEN 221",
        "credits": 3,
        "department": "Computer Science",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },

    # ============================================
    # COMPUTER SCIENCE - Advanced (400 level)
    # ============================================
    {
        "course_code": "CPSC 402",
        "title": "Numerical Linear Algebra",
        "description": "Investigation of practical techniques of computational linear algebra. Orthogonal transformations, eigenproblem solution, linear least squares.",
        "prerequisites": "One of CPSC 302, CPSC 303, or MATH 307",
        "credits": 3,
        "department": "Computer Science",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 404",
        "title": "Advanced Relational Databases",
        "description": "Physical database design, indexing, external mergesort, relational query processing and optimization, transaction processing, concurrency control, crash recovery.",
        "prerequisites": "CPSC 304; and one of CPSC 213, 261, or CPEN 212",
        "credits": 3,
        "department": "Computer Science",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 406",
        "title": "Computational Optimization",
        "description": "Formulation and analysis of algorithms for continuous and discrete optimization problems; linear, nonlinear, network, dynamic, and integer optimization; large-scale problems.",
        "prerequisites": "One of CPSC 302, CPSC 303, or MATH 307",
        "credits": 3,
        "department": "Computer Science",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 410",
        "title": "Advanced Software Engineering",
        "description": "Specification, design, construction and validation of multi-version software systems.",
        "prerequisites": "CPSC 310; or all of CPEN 321, 331",
        "credits": 3,
        "department": "Computer Science",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 411",
        "title": "Introduction to Compiler Construction",
        "description": "Practical introduction to lexical analysis, syntactic analysis, type-checking, code generation and optimization. Design and implement a compiler for a small language.",
        "prerequisites": "All of CPSC 213, 221, and 311",
        "credits": 3,
        "department": "Computer Science",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 415",
        "title": "Advanced Operating Systems",
        "description": "Process synchronization and communication schemes, virtual memory systems management, traps and interrupt handling, queuing theory, file systems.",
        "prerequisites": "One of CPSC 313 or CPEN 331",
        "credits": 3,
        "department": "Computer Science",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 416",
        "title": "Distributed Systems",
        "description": "Concepts and design of distributed systems. Communication architecture and models, process migration, naming, distributed file systems, fault tolerance, distributed transactions.",
        "prerequisites": "One of CPSC 313 or CPEN 331; and one of CPSC 317 or ELEC 331",
        "credits": 3,
        "department": "Computer Science",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 417",
        "title": "Computer Networking",
        "description": "Network protocols and architecture including internetworking, the Internet, and the OSI reference model. Layered communication protocols, routing, flow and congestion control.",
        "prerequisites": "All of CPSC 313, 317; and one of STAT 200, 201, 241, or 251",
        "credits": 3,
        "department": "Computer Science",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 418",
        "title": "Parallel Computation",
        "description": "Algorithms, architectures, and programming paradigms for parallel computation. Shared memory, message passing, data parallel architectures. Performance evaluation.",
        "prerequisites": "CPSC 320; and one of CPSC 261, 313, CPEN 212, or 411",
        "credits": 3,
        "department": "Computer Science",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 420",
        "title": "Advanced Algorithms Design and Analysis",
        "description": "Study of advanced topics in the design and analysis of algorithms and data structures. Graph-theoretic, algebraic and geometric problems; complexity issues; approximation algorithms.",
        "prerequisites": "CPSC 320",
        "credits": 3,
        "department": "Computer Science",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 421",
        "title": "Introduction to Theory of Computing",
        "description": "Characterizations of computability using machines, languages and functions. Universality, equivalence and Church's thesis. Unsolvable problems, recursive and recursively enumerable sets.",
        "prerequisites": "One of CPSC 320, MATH 220, or MATH 226",
        "credits": 3,
        "department": "Computer Science",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 422",
        "title": "Intelligent Systems",
        "description": "Principles and techniques underlying the design, implementation and evaluation of intelligent computational systems. Natural language understanding, computational vision, planning under uncertainty.",
        "prerequisites": "CPSC 322",
        "credits": 3,
        "department": "Computer Science",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 424",
        "title": "Geometric Modelling",
        "description": "Digital representation of curves and surfaces, including splines, subdivision surfaces and meshes. Algorithms for geometry representation in graphics, engineering, manufacturing.",
        "prerequisites": "One of MATH 152, 221, 223; and one of MATH 200, 217, 226, or 253",
        "credits": 3,
        "department": "Computer Science",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 425",
        "title": "Computer Vision",
        "description": "Introduction to the processing and interpretation of images. Image sensing, sampling, and filtering. Algorithms for colour analysis, texture, stereo imaging, motion interpretation.",
        "prerequisites": "All of CPSC 221, MATH 200, and MATH 221",
        "credits": 3,
        "department": "Computer Science",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 426",
        "title": "Computer Animation",
        "description": "Motion in computer graphics for characters and environments. Keyframing, inverse kinematics, particle systems, rigid body dynamics, collision detection, deformation.",
        "prerequisites": "CPSC 314",
        "credits": 3,
        "department": "Computer Science",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 427",
        "title": "Video Game Programming",
        "description": "Video game programming techniques and technologies. Rendering, animation, interaction, game AI, real-time software development, and other technical game topics.",
        "prerequisites": "CPSC 314; and one of MATH 200, 217, 226, 253; and one of MATH 152, 221, 223",
        "credits": 3,
        "department": "Computer Science",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 430",
        "title": "Computers and Society",
        "description": "The impact of computer technology on society; historical perspectives; social and economic consequences of large-scale information processing systems; professional ethics.",
        "prerequisites": "3 credits of Computer Science and third-year standing",
        "credits": 3,
        "department": "Computer Science",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 440",
        "title": "Advanced Machine Learning",
        "description": "Advanced machine learning techniques focusing on probabilistic models. Deep learning, differentiable programming, Bayesian inference, graphical models.",
        "prerequisites": "All of CPSC 320 and CPSC 340",
        "credits": 3,
        "department": "Computer Science",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 444",
        "title": "Advanced Methods for Human Computer Interaction",
        "description": "Design and evaluation methodologies and theories; formal user models including visual, motor, and information processing; HCI research frontiers.",
        "prerequisites": "CPSC 344; and one of STAT 200, 201, 203, 241, 251, BIOL 300, COMM 291, ECON 325, PSYC 218",
        "credits": 3,
        "department": "Computer Science",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 445",
        "title": "Algorithms in Bioinformatics",
        "description": "Sequence alignment, phylogenetic tree reconstruction, prediction of RNA and protein structure, gene finding and sequence annotation, gene expression analysis.",
        "prerequisites": "CPSC 320; and either BMEG 250 or 6 credits of BIOL beyond BIOL 111",
        "credits": 3,
        "department": "Computer Science",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 447",
        "title": "Introduction to Visualization",
        "description": "Design and implementation of static and interactive visualizations. Selection of appropriate visualization methods and assessment per design principles.",
        "prerequisites": "One of CPSC 310 or CPEN 321",
        "credits": 3,
        "department": "Computer Science",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 455",
        "title": "Applied Industry Practices",
        "description": "Hands-on project, mentored by industry experts, integrating skills relevant to early career: technical skills, communication, teamwork, networking.",
        "prerequisites": "One of CPSC 310 or CPEN 321",
        "credits": 3,
        "department": "Computer Science",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },

    # ============================================
    # COMPUTER SCIENCE - Graduate Level (500+)
    # ============================================
    {
        "course_code": "CPSC 500",
        "title": "Fundamentals of Algorithm Design and Analysis",
        "description": "Graduate-level study of algorithm design paradigms and analysis techniques. Advanced topics in algorithmic theory and practice.",
        "prerequisites": "Graduate standing or permission of instructor",
        "credits": 3,
        "department": "Computer Science",
        "level": "Graduate",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 502",
        "title": "Artificial Intelligence I",
        "description": "Graduate-level introduction to artificial intelligence. Advanced topics in search, planning, knowledge representation, and reasoning.",
        "prerequisites": "Graduate standing or permission of instructor",
        "credits": 3,
        "department": "Computer Science",
        "level": "Graduate",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 503",
        "title": "Computational Linguistics I",
        "description": "Introduction to computational approaches to natural language. Morphology, syntax, semantics, and discourse processing.",
        "prerequisites": "Graduate standing or permission of instructor",
        "credits": 3,
        "department": "Computer Science",
        "level": "Graduate",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 504",
        "title": "Data Management",
        "description": "Graduate-level study of data management systems. Query processing, transaction management, distributed databases.",
        "prerequisites": "Graduate standing or permission of instructor",
        "credits": 3,
        "department": "Computer Science",
        "level": "Graduate",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 522",
        "title": "Artificial Intelligence II",
        "description": "Advanced topics in artificial intelligence including probabilistic reasoning, machine learning theory, and cognitive architectures.",
        "prerequisites": "CPSC 502 or permission of instructor",
        "credits": 3,
        "department": "Computer Science",
        "level": "Graduate",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 532",
        "title": "Topics in Artificial Intelligence",
        "description": "Selected advanced topics in AI. May include deep learning, reinforcement learning, multimodal learning, LLMs, or other emerging areas.",
        "prerequisites": "Graduate standing and permission of instructor",
        "credits": 3,
        "department": "Computer Science",
        "level": "Graduate",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 540",
        "title": "Machine Learning",
        "description": "Graduate-level machine learning covering supervised and unsupervised learning, neural networks, kernel methods, and probabilistic models.",
        "prerequisites": "Graduate standing or permission of instructor",
        "credits": 3,
        "department": "Computer Science",
        "level": "Graduate",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 544",
        "title": "Human Computer Interaction",
        "description": "Graduate-level study of human-computer interaction. User-centered design, evaluation methods, and emerging interaction paradigms.",
        "prerequisites": "Graduate standing or permission of instructor",
        "credits": 3,
        "department": "Computer Science",
        "level": "Graduate",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 545",
        "title": "Algorithms for Bioinformatics",
        "description": "Graduate-level computational biology and bioinformatics. Sequence analysis, structural biology, systems biology.",
        "prerequisites": "Graduate standing or permission of instructor",
        "credits": 3,
        "department": "Computer Science",
        "level": "Graduate",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 547",
        "title": "Information Visualization",
        "description": "Graduate-level study of information visualization. Theory, design principles, and implementation of visualization systems.",
        "prerequisites": "Graduate standing or permission of instructor",
        "credits": 3,
        "department": "Computer Science",
        "level": "Graduate",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "CPSC 550",
        "title": "Machine Learning II",
        "description": "Advanced machine learning including deep learning architectures, generative models, and reinforcement learning.",
        "prerequisites": "CPSC 540 or permission of instructor",
        "credits": 3,
        "department": "Computer Science",
        "level": "Graduate",
        "source": "UBC Academic Calendar"
    },

    # ============================================
    # STATISTICS - Relevant to ML/AI
    # ============================================
    {
        "course_code": "STAT 200",
        "title": "Elementary Statistics for Applications",
        "description": "Classical, nonparametric, and robust inferences about location, scale, means, proportions, and relations. Emphasis on interpretation of data and statistical thinking.",
        "prerequisites": "One of MATH 11, Pre-calculus 11, or Foundations of Mathematics 11",
        "credits": 3,
        "department": "Statistics",
        "level": "Second Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "STAT 201",
        "title": "Statistical Inference for Data Science",
        "description": "Classical, nonparametric, and simulation-based techniques for estimation and hypothesis testing, focusing on data science applications.",
        "prerequisites": "One of DSCI 100 or STAT 200",
        "credits": 3,
        "department": "Statistics",
        "level": "Second Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "STAT 300",
        "title": "Intermediate Statistics for Applications",
        "description": "Further topics in statistical inference including analysis of variance, regression, and categorical data analysis.",
        "prerequisites": "STAT 200",
        "credits": 3,
        "department": "Statistics",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "STAT 301",
        "title": "Statistical Modelling for Data Science",
        "description": "Modern approaches to regression analysis for data science. Model selection, regularization, and interpretation of results.",
        "prerequisites": "STAT 201 and one of CPSC 203, CPSC 210, or DSCI 100",
        "credits": 3,
        "department": "Statistics",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "STAT 302",
        "title": "Introduction to Probability",
        "description": "Basic notions of probability, random variables, expectation and conditional expectation, laws of large numbers.",
        "prerequisites": "One of MATH 200, MATH 217, MATH 226, or MATH 253",
        "credits": 3,
        "department": "Statistics",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "STAT 305",
        "title": "Introduction to Statistical Inference",
        "description": "Parametric estimation, hypothesis testing, confidence intervals, and Bayesian inference.",
        "prerequisites": "STAT 302 or MATH 302",
        "credits": 3,
        "department": "Statistics",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "STAT 306",
        "title": "Finding Relationships in Data",
        "description": "Modelling a response variable as a function of several explanatory variables: multiple regression for continuous responses, logistic regression for binary responses.",
        "prerequisites": "STAT 200 and one of MATH 152, MATH 221, MATH 223",
        "credits": 3,
        "department": "Statistics",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "STAT 406",
        "title": "Methods for Statistical Learning",
        "description": "Flexible, data-adaptive methods for regression and classification: smoothing methods, neural networks, tree-based methods, boosting and bagging, model selection.",
        "prerequisites": "STAT 306",
        "credits": 3,
        "department": "Statistics",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "STAT 443",
        "title": "Time Series and Forecasting",
        "description": "Trend and seasonality, stationary and non-stationary processes, autoregressive moving average models, estimation and forecasting, spectrum analysis.",
        "prerequisites": "One of STAT 305, STAT 344; and one of MATH 302, STAT 302",
        "credits": 3,
        "department": "Statistics",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "STAT 450",
        "title": "Case Studies in Statistics",
        "description": "Readings and projects in areas of current statistical application such as genetics, epidemiology, and public health.",
        "prerequisites": "STAT 306 and one of STAT 305 or MATH 302 or STAT 302",
        "credits": 3,
        "department": "Statistics",
        "level": "Fourth Year",
        "source": "UBC Academic Calendar"
    },

    # ============================================
    # DATA SCIENCE - DSCI Courses
    # ============================================
    {
        "course_code": "DSCI 100",
        "title": "Introduction to Data Science",
        "description": "Use of data science tools to summarize, visualize, and analyze data. Sensible workflows and clear interpretations are emphasized.",
        "prerequisites": "MATH 12",
        "credits": 3,
        "department": "Data Science",
        "level": "First Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "DSCI 310",
        "title": "Reproducible and Trustworthy Workflows for Data Science",
        "description": "Best practices for creating reproducible data analyses. Version control, containerization, testing, and workflow automation.",
        "prerequisites": "DSCI 100 or STAT 201",
        "credits": 3,
        "department": "Data Science",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },

    # ============================================
    # MATHEMATICS - Relevant to ML/AI
    # ============================================
    {
        "course_code": "MATH 221",
        "title": "Matrix Algebra",
        "description": "Systems of linear equations, operations on matrices, determinants, eigenvalues and eigenvectors, diagonalization of symmetric matrices.",
        "prerequisites": "One of MATH 12, Pre-calculus 12",
        "credits": 3,
        "department": "Mathematics",
        "level": "Second Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "MATH 307",
        "title": "Applied Linear Algebra",
        "description": "Applications of linear algebra including linear programming, Markov chains, linear regression, principal component analysis, singular value decomposition.",
        "prerequisites": "One of MATH 152, MATH 221, MATH 223",
        "credits": 3,
        "department": "Mathematics",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },
    {
        "course_code": "MATH 340",
        "title": "Introduction to Linear Programming",
        "description": "Linear programming models, the simplex method, duality, sensitivity analysis, applications to network flows, integer programming.",
        "prerequisites": "One of MATH 152, MATH 221, MATH 223",
        "credits": 3,
        "department": "Mathematics",
        "level": "Third Year",
        "source": "UBC Academic Calendar"
    },
]


def save_courses(output_path: Path):
    """Save courses to JSON file with metadata."""
    output_data = {
        "metadata": {
            "source": "UBC Academic Calendar",
            "url": "https://vancouver.calendar.ubc.ca/course-descriptions",
            "collected_date": datetime.now().isoformat(),
            "total_courses": len(COURSES),
            "description": "Curated UBC courses focused on Computer Science, Data Science, Statistics, and Mathematics - relevant for AI/ML career paths"
        },
        "courses": COURSES
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Saved {len(COURSES)} courses to {output_path}")


def print_summary():
    """Print summary statistics about the course data."""
    departments = {}
    levels = {}

    for course in COURSES:
        dept = course.get('department', 'Unknown')
        level = course.get('level', 'Unknown')

        departments[dept] = departments.get(dept, 0) + 1
        levels[level] = levels.get(level, 0) + 1

    print("\n" + "=" * 50)
    print("UBC COURSE DATA SUMMARY")
    print("=" * 50)
    print(f"\nTotal courses: {len(COURSES)}")
    print(f"Source: UBC Academic Calendar")
    print(f"URL: https://vancouver.calendar.ubc.ca/course-descriptions")

    print("\nBy Department:")
    for dept, count in sorted(departments.items(), key=lambda x: -x[1]):
        print(f"  {dept}: {count}")

    print("\nBy Level:")
    level_order = ["First Year", "Second Year", "Third Year", "Fourth Year", "Graduate"]
    for level in level_order:
        if level in levels:
            print(f"  {level}: {levels[level]}")

    # Print some sample courses for verification
    print("\n" + "=" * 50)
    print("SAMPLE COURSES (AI/ML focused)")
    print("=" * 50)
    ai_courses = [c for c in COURSES if any(kw in c['title'].lower() or kw in c['description'].lower()
                                            for kw in ['machine learning', 'artificial intelligence', 'neural', 'deep learning'])]
    for course in ai_courses[:5]:
        print(f"\n{course['course_code']}: {course['title']}")
        print(f"  Credits: {course['credits']}, Level: {course['level']}")
        print(f"  {course['description'][:100]}...")


if __name__ == "__main__":
    output_path = Path(__file__).parent.parent / "data" / "courses.json"
    save_courses(output_path)
    print_summary()
