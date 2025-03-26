import os
import random
from flask import Blueprint, render_template, request, jsonify
from langchain.chains import LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq

chatbot = Blueprint("chatbot", __name__, template_folder="templates", static_folder="static")

# get groq API key from environment variable
groq_api_key = "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"

if not groq_api_key:
    raise ValueError("Groq API key not found. Please set the 'GROQ_API_KEY' environment variable.")

# initialize groq langchain chat object
groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name='llama3-8b-8192')

# initialize conversation memory
memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history", return_messages=True)

@chatbot.route("/chat", methods=["GET"])
def chat():
    return render_template("chat.html")

@chatbot.route("/ask", methods=["POST"])
def ask():
    user_question = request.form["question"]

    # construct a chat prompt template using various components
    prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{human_input}")
        ]
    )
    
    # create a conversation chain 
    conversation = LLMChain(
        llm=groq_chat,
        prompt=prompt,
        verbose=True,
        memory=memory,
    )

    # generate chatbots answer 
    response = conversation.predict(human_input=user_question)
    memory.save_context({'input': user_question}, {'output': response})

    formatted_response = format_response(response)

    return jsonify({"response": formatted_response})

def format_response(response):
    
    return response.replace('\n', '<br>')

class ChatGroq:
    def __init__(self, groq_api_key, model_name):
        self.groq_api_key = groq_api_key
        self.model_name = model_name

    def get_recommendations(self, stock_data):
        recommendations = {}
        for stock in stock_data:
            # recommendation based on stock price
            if stock['price'] < 50:
                recommendations[stock['company']] = "Strong Buy"
            elif 50 <= stock['price'] < 100:
                recommendations[stock['company']] = "Buy"
            elif 100 <= stock['price'] < 150:
                recommendations[stock['company']] = "Hold"
            elif 150 <= stock['price'] < 200:
                recommendations[stock['company']] = "Sell"
            else:
                recommendations[stock['company']] = "Strong Sell"
        return recommendations
    
    def generate_knowledge(self, topic):
        # Example dynamic content generation
        intro = f"This {topic} would cover various aspects including history, key concepts, influential figures, and current trends."
        sections = [
            f"Financial markets: Understanding financial markets is essential for grasping the broader economic landscape. This includes stock, bond, and derivatives markets, each with unique functions crucial to economic understanding. The stock market involves trading shares of publicly traded companies, its pricing driven by supply and demand. Participants like investors, market makers, and brokers ensure market liquidity. The bond market, encompassing government and corporate bonds, facilitates capital raising, influenced by factors like interest rates and credit ratings. Intermediaries like underwriters and rating agencies aid in risk assessment. Derivatives, including options and futures, offer risk management and speculative tools, tied to underlying assets like stocks or commodities. Hedgers, speculators, and arbitrageurs engage in this market. Understanding market dynamics is vital as they impact investment decisions, consumer confidence, and economic stability. Exploring the interconnectedness of markets and their participants is crucial for navigating the financial world effectively, whether as an investor, policymaker, or informed citizen.",
            f"Investment strategies encompass various approaches, including value investing, growth investing, and index investing, each with distinct principles, advantages, and limitations. Value investing focuses on finding undervalued assets, purchasing them at a discount to their intrinsic value. It involves thorough analysis of financial metrics and company fundamentals. While value investing can offer opportunities for significant returns, it requires patience and discipline, as undervalued stocks may take time to realize their full potential.On the other hand, growth investing emphasizes investing in companies with strong growth potential, even if their current valuations appear high. This strategy seeks to capitalize on future earnings growth, often associated with innovative industries or disruptive technologies. Growth investing can lead to substantial gains, but it carries higher risk due to the uncertainty of future performance and market volatility.Index investing involves tracking a market index, such as the S&P 500, by investing in a portfolio that mirrors its composition. This passive approach offers diversification and typically lower fees compared to actively managed funds. Index investing is suitable for investors seeking broad market exposure with minimal effort and research.Each strategy has its advantages and limitations. Value investing may require patience and may not always yield immediate results. Growth investing entails higher risk but can lead to significant returns for investors willing to take on volatility. Index investing provides simplicity and diversification but may limit potential upside compared to actively managed strategies.Ultimately, investors should carefully assess their financial goals, risk tolerance, and time horizon when selecting an investment strategy. Diversification across multiple strategies may also be prudent to manage risk effectively.",
            f"Economic theories: This section explores influential economic theories shaping financial markets and investment decisions. The efficient market hypothesis posits that asset prices reflect all available information, making it impossible to consistently outperform the market. Behavioral finance, however, challenges this notion, emphasizing psychological factors driving market behavior, such as irrational exuberance or panic. Understanding these behavioral biases can help investors identify mispriced assets and exploit market inefficiencies. Supply and demand dynamics, fundamental to market economics, dictate price movements based on the balance between buyers and sellers. Changes in supply or demand can affect asset prices, influencing investment strategies.Efficient market hypothesis suggests that trying to beat the market is futile, advocating for passive investment strategies like index funds. Conversely, behavioral finance recognizes market inefficiencies stemming from human behavior, encouraging active management to exploit these inefficiencies for profit. Supply and demand dynamics influence market sentiment and asset valuations, guiding investors in assessing investment opportunities.By comprehensively understanding these theories, investors can better navigate financial markets and make informed investment decisions. Acknowledging the efficient market hypothesis may lead to adopting a passive investment approach, while insights from behavioral finance can inform active investment strategies. Recognizing supply and demand dynamics aids in assessing market trends and identifying potential investment opportunities. Integrating these theories into financial analysis enhances decision-making processes, helping investors achieve their financial goals while managing risks effectively.",
            f"Impact of global events: Global events such as economic crises, political shifts, and technological advancements wield significant influence over financial systems. This section delves into their interconnectedness, transmission mechanisms of shocks, and risk management strategies.Economic crises, like the 2008 financial meltdown, showcase how disruptions in one part of the world reverberate globally through interconnected financial systems. Political changes, such as elections or geopolitical tensions, can trigger market volatility as investors reassess risk perceptions. Technological advancements, like the rise of fintech or AI-driven trading, reshape market structures, altering trading patterns and risk landscapes.Understanding the interconnectedness of global markets is crucial. A crisis in one country can trigger a domino effect, impacting economies worldwide. Transmission mechanisms vary—from direct financial linkages to sentiment contagion through media and social networks.Effective risk management strategies are essential for mitigating the impact of global events. Diversification across asset classes and geographical regions helps spread risk. Hedging techniques, such as derivatives or currency forwards, can protect against adverse movements. Constant monitoring of geopolitical and macroeconomic developments enables proactive adjustments to investment portfolios.In sum, global events exert profound effects on financial systems, necessitating a comprehensive understanding of interconnectedness and robust risk management strategies. Adaptability and vigilance are key for investors and financial institutions to navigate the complexities of an ever-evolving global landscape.",
            f"Financial instruments:This section provides an overview of key financial instruments, including stocks, bonds, mutual funds, and exchange-traded funds (ETFs). It explores their characteristics, valuation methods, and risk-return profiles, as well as their role in constructing diversified portfolios.Stocks represent ownership in a company and offer potential for capital appreciation and dividends. Valuation methods include fundamental analysis, assessing company financials, and technical analysis, studying price trends. Stocks generally carry higher risk but also offer higher potential returns.Bonds are debt securities issued by governments or corporations, providing fixed interest payments and repayment of principal at maturity. Valuation methods involve analyzing credit ratings, interest rates, and yield curves. Bonds are typically less risky than stocks but offer lower returns.Mutual funds pool money from multiple investors to invest in a diversified portfolio of stocks, bonds, or other assets. They offer professional management and diversification but often come with management fees and potential performance limitations.ETFs are similar to mutual funds but trade on stock exchanges like individual stocks. They provide diversification, liquidity, and typically lower fees than mutual funds. ETFs track various indices or sectors and offer flexibility in trading.Constructing a diversified portfolio involves allocating assets across different classes to manage risk and optimize returns. Stocks offer growth potential but higher volatility, while bonds provide stability and income. Mutual funds and ETFs offer diversification and professional management across multiple asset classes.Investors should consider their risk tolerance, investment goals, and time horizon when selecting financial instruments. Diversification across stocks, bonds, mutual funds, and ETFs helps spread risk and maximize long-term returns. Regular review and rebalancing of the portfolio are essential to adapt to changing market conditions and investor objectives.",
            f"Risk management: This section explores strategies for effectively managing financial risk, encompassing diversification, hedging, and insurance. It discusses the concept of risk, its various types and sources, and techniques for identifying, assessing, and mitigating risks in investment and business activities.Risk is inherent in all financial endeavors, arising from uncertainties in market conditions, economic factors, regulatory changes, and unforeseen events. Types of risk include market risk, which stems from fluctuations in asset prices; credit risk, associated with potential defaults by counterparties; liquidity risk, arising from the inability to quickly convert assets into cash; and operational risk, related to internal processes and systems failures.Diversification involves spreading investments across different assets or sectors to reduce overall portfolio risk. By allocating resources across diverse investments, investors can minimize the impact of adverse events affecting any single asset or sector. This strategy aims to achieve a balance between risk and return by not putting all eggs in one basket.Hedging is another risk management technique that involves offsetting potential losses in one position by taking an opposite position in another asset or derivative. For example, investors can hedge against fluctuations in currency exchange rates or commodity prices to protect against adverse movements that could negatively impact their investments.Insurance provides another layer of protection against financial losses resulting from unforeseen events such as accidents, natural disasters, or liability claims. By transferring risk to an insurance provider in exchange for premiums, individuals and businesses can mitigate the financial impact of unexpected events.Overall, effective risk management involves a combination of diversification, hedging, and insurance strategies tailored to specific investment objectives and risk tolerances. By identifying, assessing, and mitigating risks, investors and businesses can safeguard their financial well-being and enhance the likelihood of achieving their goals in an unpredictable and dynamic economic environment.",
            f"Financial analysis: This section delves into techniques for analyzing financial data and making informed investment decisions, including financial statement analysis, ratio analysis, discounted cash flow (DCF) analysis, and other methods employed by analysts and investors to assess the performance and value of companies and assets.Financial statement analysis involves scrutinizing a company's financial reports, including the income statement, balance sheet, and cash flow statement, to evaluate its financial health and performance over time. Analysts examine key metrics such as revenue growth, profitability, liquidity, and solvency to gauge the company's ability to generate returns and meet its financial obligations.Ratio analysis involves calculating and interpreting various financial ratios to gain insights into a company's operational efficiency, financial leverage, and overall performance. Common ratios include profitability ratios (e.g., return on equity), liquidity ratios (e.g., current ratio), and leverage ratios (e.g., debt-to-equity ratio), which provide valuable benchmarks for comparing companies within the same industry or sector.Discounted cash flow (DCF) analysis is a valuation method used to estimate the intrinsic value of a company or asset by forecasting its future cash flows and discounting them back to their present value using an appropriate discount rate. DCF analysis helps investors assess the attractiveness of an investment opportunity based on its expected returns relative to its current market price.Other methods used by analysts and investors include comparative analysis, where companies are compared against their peers or industry benchmarks, and scenario analysis, which involves evaluating the potential impact of various economic or market scenarios on investment outcomes.By employing these techniques, analysts and investors can gain a comprehensive understanding of companies and assets, identify investment opportunities, and make informed decisions that align with their investment objectives and risk tolerance. Effective financial analysis enables investors to capitalize on market inefficiencies, mitigate risks, and optimize returns in an increasingly complex and dynamic investment landscape.",
            f"Regulatory environment: This section provides an overview of the regulatory framework governing financial markets and institutions, emphasizing the role of regulatory bodies, key regulations and standards, and compliance requirements aimed at promoting transparency, stability, and investor protection.Regulatory bodies, such as the Securities and Exchange Commission (SEC) in the United States, the Financial Conduct Authority (FCA) in the United Kingdom, and the European Securities and Markets Authority (ESMA) in the European Union, oversee financial markets and enforce regulations to ensure fair and orderly conduct.Key regulations and standards include laws like the Dodd-Frank Act in the US, the Markets in Financial Instruments Directive (MiFID II) in the EU, and the Basel III framework for banking regulation. These regulations address various aspects of financial markets and institutions, such as market integrity, capital adequacy, risk management, and consumer protection.",
            f"Behavioral finance: Awareness of these psychological factors is essential for improving decision-making. By recognizing cognitive biases and emotional triggers, investors can employ strategies to mitigate their impact. This may involve implementing disciplined investment processes, setting clear investment goals, and maintaining a long-term perspective despite short-term market fluctuations.Furthermore, education and understanding of behavioral finance concepts can empower investors to make more informed decisions. Techniques like mindfulness and self-reflection can help individuals become more aware of their own biases and emotions, enabling them to make rational and objective investment choices.Ultimately, by acknowledging and addressing the psychological factors that influence financial decision-making, investors can enhance their ability to navigate markets effectively, avoid common pitfalls, and achieve their long-term financial goals.",
            f"Ethical considerations: Social responsibility refers to a company's obligation to act in the best interests of society beyond its legal requirements. Ethical issues in social responsibility include environmental stewardship, labor practices, and community engagement. Companies are increasingly being held accountable for their impact on the environment, treatment of employees, and contribution to the communities in which they operate.Sustainability focuses on the long-term viability of business practices, considering their economic, social, and environmental impacts. Ethical issues in sustainability include resource depletion, climate change, and responsible investment practices. Investors are increasingly integrating environmental, social, and governance (ESG) factors into their investment decisions, driving companies to adopt more sustainable business practices.Ethical dilemmas in finance also extend to investors and regulators. Investors face challenges in balancing financial returns with ethical considerations, such as avoiding investments in industries with negative social or environmental impacts. Regulators must establish and enforce standards that promote transparency, integrity, and fairness in financial markets while balancing the interests of various stakeholders.Principles and standards that guide ethical behavior and corporate governance practices include transparency, accountability, fairness, and integrity. Codes of conduct, industry regulations, and voluntary initiatives, such as the Principles for Responsible Investment (PRI) and the Global Reporting Initiative (GRI), provide frameworks for ethical decision-making and reporting practices."
        ]
        
        body = "\n\n".join(random.sample(sections, k=5))  # Selecting 5 random sections
        essay = f"{intro}\n\n{body}"
        return essay

        



