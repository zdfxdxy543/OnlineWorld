const papers = [
  {
    paper_id: 'p001',
    title: 'Deep Learning Based Natural Language Processing Research',
    authors: ['Zhang San', 'Li Si'],
    institution: 'Tsinghua University',
    journal: 'Journal of Computers',
    publish_date: '2000-03-15',
    abstract: 'This paper proposes a deep learning based natural language processing method that improves text classification accuracy by modifying the structure of recurrent neural networks. Experimental results show that the method achieves significant performance improvements on multiple benchmark datasets.',
    keywords: ['Deep Learning', 'Natural Language Processing', 'Recurrent Neural Network', 'Text Classification'],
    downloads: 1523,
    pages: 12,
    file_size: 2048576,
    file_name: 'zhangsan_nlp_2000.pdf',
  },
  {
    paper_id: 'p002',
    title: 'E-commerce Website User Experience Optimization Strategy Research',
    authors: ['Wang Wu', 'Liu Liu'],
    institution: 'Peking University',
    journal: 'Journal of Information Systems',
    publish_date: '1999-08-20',
    abstract: 'With the rapid development of the Internet, user experience on e-commerce websites has become increasingly important. Through analysis of existing e-commerce websites, this paper proposes a series of user experience optimization strategies, including improvements in interface design, navigation structure, and payment processes.',
    keywords: ['E-commerce', 'User Experience', 'Website Optimization', 'Human-Computer Interaction'],
    downloads: 892,
    pages: 8,
    file_size: 1536000,
    file_name: 'wangwu_ecommerce_1999.pdf',
  },
  {
    paper_id: 'p003',
    title: 'Design and Implementation of Distributed Database Systems',
    authors: ['Zhou Qi', 'Wu Ba', 'Zheng Jiu'],
    institution: 'Shanghai Jiao Tong University',
    journal: 'Journal of Software',
    publish_date: '1999-11-10',
    abstract: 'This paper introduces the design and implementation of a new distributed database system. The system adopts a three-tier architecture and supports features such as data sharding, load balancing, and fault recovery. Experiments show that the system performs well in both performance and reliability.',
    keywords: ['Distributed Database', 'Data Sharding', 'Load Balancing', 'Fault Recovery'],
    downloads: 2341,
    pages: 15,
    file_size: 3145728,
    file_name: 'liu_distributed_1999.pdf',
  },
  {
    paper_id: 'p004',
    title: 'Application of Artificial Intelligence in Medical Imaging Diagnosis',
    authors: ['Sun Shi', 'Wu Shiyi'],
    institution: 'Zhejiang University',
    journal: 'Computer Application Research',
    publish_date: '2000-01-05',
    abstract: 'Medical imaging diagnosis is one of the important application areas of artificial intelligence technology. This paper proposes a convolutional neural network based medical image classification method that can automatically identify lesion areas in X-rays. Experimental results show that the method achieves a diagnostic accuracy rate of over 92%.',
    keywords: ['Artificial Intelligence', 'Medical Imaging', 'Convolutional Neural Network', 'Computer-Aided Diagnosis'],
    downloads: 3102,
    pages: 10,
    file_size: 2621440,
    file_name: 'sun_medical_2000.pdf',
  },
  {
    paper_id: 'p005',
    title: 'Network Security Firewall Technology Research',
    authors: ['Zheng Shier'],
    institution: 'University of Science and Technology of China',
    journal: 'Computer Engineering',
    publish_date: '1998-06-18',
    abstract: 'Firewall is the first line of defense in network security. This paper analyzes in detail the advantages and disadvantages of existing firewall technology and proposes an improved firewall scheme based on state inspection. This scheme can effectively prevent various network attacks and improve network security.',
    keywords: ['Network Security', 'Firewall', 'State Inspection', 'Intrusion Detection'],
    downloads: 1876,
    pages: 9,
    file_size: 1843200,
    file_name: 'zheng_firewall_1998.pdf',
  },
  {
    paper_id: 'p006',
    title: 'Web Data Mining Technology and Its Applications',
    authors: ['Qian Shisan', 'Feng Shisi'],
    institution: 'Fudan University',
    journal: 'Data Mining and Knowledge Discovery',
    publish_date: '1999-04-22',
    abstract: 'With the popularization of the World Wide Web, Web data mining has become a hot research direction in the field of information processing. This paper discusses Web log mining, page structure mining and Web content mining technologies, and provides specific application cases.',
    keywords: ['Data Mining', 'Web Mining', 'Information Retrieval', 'Knowledge Discovery'],
    downloads: 1456,
    pages: 11,
    file_size: 2359296,
    file_name: 'qian_webmining_1999.pdf',
  },
]

const categories = [
  { id: 'computer', name: 'Computer Science', count: 45 },
  { id: 'medicine', name: 'Medicine', count: 32 },
  { id: 'economics', name: 'Economics', count: 28 },
  { id: 'education', name: 'Education', count: 21 },
  { id: 'engineering', name: 'Engineering', count: 38 },
  { id: 'law', name: 'Law', count: 15 },
]

function getPapers(query = null) {
  return new Promise((resolve) => {
    setTimeout(() => {
      if (!query) {
        resolve(papers)
        return
      }
      const q = query.toLowerCase()
      const filtered = papers.filter(p => 
        p.title.toLowerCase().includes(q) ||
        p.abstract.toLowerCase().includes(q) ||
        p.keywords.some(k => k.toLowerCase().includes(q))
      )
      resolve(filtered)
    }, 300)
  })
}

function getPaperById(paperId) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const paper = papers.find(p => p.paper_id === paperId)
      if (paper) {
        resolve(paper)
      } else {
        reject(new Error('Paper not found'))
      }
    }, 200)
  })
}

function getHotPapers(limit = 5) {
  return new Promise((resolve) => {
    setTimeout(() => {
      const sorted = [...papers].sort((a, b) => b.downloads - a.downloads)
      resolve(sorted.slice(0, limit))
    }, 200)
  })
}

function getCategories() {
  return new Promise((resolve) => {
    setTimeout(() => resolve(categories), 100)
  })
}

function getDownloadUrl(paperId) {
  return `/api/v1/academic/download/${paperId}`
}

export {
  getPapers,
  getPaperById,
  getHotPapers,
  getCategories,
  getDownloadUrl,
}
