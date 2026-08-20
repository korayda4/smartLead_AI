class FallbackService:
    def get(self, msg: str) -> str:
        m = msg.lower()

        if any(k in m for k in ["deprem", "çanta", "kit"]):
            return (
                "72 saatlik afet kitimiz; su, yiyecek, ilk yardım malzemeleri, el feneri ve powerbank içerir. "
                "Aile büyüklüğünüze göre farklı paketlerimiz mevcuttur."
            )
        if any(k in m for k in ["mesh", "haberleşme", "bluetooth", "wifi", "bt", "internet"]):
            return (
                "İnternetsiz BT/Wi-Fi Mesh ağımız, afet sırasında GSM çöktüğünde telefonları birbirine bağlar. "
                "Afetzede Modu SOS sinyali, Kurtarıcı Modu konum paylaşımı sağlar."
            )
        if any(k in m for k in ["yangın", "yangin", "risk", "bölge", "fay", "sismik", "istanbul", "nerede"]):
            return (
                "Bölgenizin fay hattı mesafesi, zemin yapısı ve yangın tahliye rotasını analiz edip "
                "özel risk raporu sunuyoruz."
            )
        if any(k in m for k in ["fiyat", "ücret", "para", "kaç", "maliyet"]):
            return "Fiyatlarımız kit içeriğine ve aile büyüklüğüne göre değişmektedir. Daha fazla bilgi için web sitemizi inceleyebilirsiniz."

        return (
            "Deprem/yangın erken uyarı, internetsiz Mesh haberleşme ve 72 saatlik afet kitleri konusunda yardımcıyım. "
            "Hangi konuda bilgi almak istersiniz?"
        )
