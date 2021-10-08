% Analysis for psychometric function


addpath('/NOBACKUP2/Pred_spec/Palamedes')


%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%      For thermal and mechano irrespective or expectation %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

ntrialseachcond = 27*2;
sessiontype = 2; % 1 type, 2 location

nlevels = 5;
% extract data


% Trial types

% Expectation / Pain type presented

% 1 {'ThermalHigh_thermal'} - 12 trials-pt
% 2 {'ThermalHigh_mechano'} - 6 trials-pt
% 3 {'MechanoHigh_mechano'} - 12 trials-pt
% 4 {'MechanoHigh_thermal'} - 6 trials-pt
% 5 {'Noexpect_thermal'} - 9 trials-pt
% 6 {'Noexpect_mechano'} - 9 trials-pt
% 


% Can analyse thermal and mechano irrespective of expectation condition
% so cond 1 = thermal (1, 4, 5)
% cond 2 = mechano (2, 3, 6)




session1 = [48.4580678851175, ...
49.144316797215, ...
49.8305657093124, ...
50.5168146214099, ...
51.2030635335074];

session2 = [48.7086369834031, ...
49.6354553575626, ...
50.5622737317222, ...
51.4890921058818, ...
52.4159104800414
];

%datapsychophys2thermsW30PainType20210722T14
levels = [48.5 49.4 50.3 51.3 52.2];
%dataTestingPainLocW30PainLocation20210802T17
%levels = [47.2 47.9 48.6 49.3 50.0];

%levels debug
%levels = [15, 25, 40, 45, 50];
%levels = [40, 42, 44, 46, 48, 50, 52, 54, 56];

comparison_intensity_thermal = round(levels,1)

comparison_intensity_mechano =  [32, 64, 128, 256, 512]


%conditions_all_expects = nan(2,ntrialseachcond,5);



%conditions = nan(5,ntrialseachcond,5);
tmp = [];
results = nan(5,1,2);
for condition = 1:2; %conditions
%     conditions(:,i) = find(subjectdata(:,1) == i); %find all intact trials, all BS trials...
%     tmp(:,i) = find(subjectdata(:,1) == i);
    for intensity = 1:nlevels %intensity
%       SFs(:,j) = find(subjectdata(:,2) == j);
%         conditions(j,:,i) = find(subjectdata(tmp(:,i),2) == j);
%         conditions(j,:,i) = find(subjectdata(tmp(:,i),2) == j);
%         tmp2(:,j) = find(subjectdata(:,2) == j);
%         subjectdata(tmp,tmp2)
        if condition == 1 %thermal
            tmp = find( ... 
                ( (data.TrialTypeID == 1) | (data.TrialTypeID == 4) | (data.TrialTypeID == 5) ) & ...
            data.ComparisonIntensity == comparison_intensity_thermal(intensity)  & ...
            data.SubRespComparisonMorePain == 1    ); % find condition 1, 4 or 5 where comparison intensity is the required one
            % and the response was 1, meaning comparison more pain
        else % mechano
            if sessiontype == 1
                tmp = find( ...
                ( (data.TrialTypeID == 2) | (data.TrialTypeID == 3) | (data.TrialTypeID == 6) ) & ...
                 data.ComparisonIntensity == comparison_intensity_mechano(intensity)  & ...
                 data.SubRespComparisonMorePain == 1    ); % find condition 2, 3 or 6 where comparison intensity is the required one
            else
                tmp = find( ...
                ( (data.TrialTypeID == 2) | (data.TrialTypeID == 3) | (data.TrialTypeID == 6) ) & ...
                 data.ComparisonIntensity == comparison_intensity_thermal(intensity)  & ...
                 data.SubRespComparisonMorePain == 1    ); % find condition 2, 3 or 6 where comparison intensity is the required one
            end
                % and the response was 1, meaning comparison more pain
        end
        
        
        
        
        %(:,2) == j) & (subjectdata(:,1) == i) & subjectdata(:,3) == 2)';
%         conditions(j,:,i) = tmp;
        results(intensity,1,condition) = size(tmp,1);

    end
end



%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%      For thermal and mechano irrespective or expectation %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% figure
figure; plot(1:nlevels, results(1:nlevels,1,1), 'ro-') %Thermal
hold on;
plot(1:nlevels, results(1:nlevels,1,2), 'bs-') % Mechano
%plot(1:5, results(1:5,1,3), 'go-') %occl
%plot(1:5, results(1:5,1,4), 'kx-') %del sharp
%plot(1:5, results(1:5,1,5), 'cx-') %del fuzzy
axis([0.5 nlevels+0.5 -0.5 ntrialseachcond+0.5])
if sessiontype == 1
    [leg] = legend('Thermal', 'Mechano', 'Location', 'Northwest');
elseif sessiontype == 2
    [leg] = legend('Left', 'Right', 'Location', 'Northwest');
end
ax = findobj(gcf,'type','axes'); %Retrieve the axes to be copied
hold off;

colorpoints(1) = 'r';
colorpoints(2) = 'b';
colorpoints(3) = 'g';
colorpoints(4) = 'k';
colorpoints(5) = 'c';

markershape(1) = 's';
markershape(2) = 's';
markershape(3) = 'o';
markershape(4) = 'x';
markershape(5) = 'x';



%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%      For thermal and mechano irrespective or expectation %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% palamedes analysis

%add path
addpath('/NOBACKUP2/Pred_spec/Palamedes') 

disp ('Palamedes...')
%Stimulus intensities
StimLevels = comparison_intensity_thermal; 
figure('name','Maximum Likelihood Psychometric Function Fitting');
    axes
    hold on

for condition = 1:1 %conditions
    
    %Number of positive responses (e.g., 'yes' or 'correct' at each of the
    %   entries of 'StimLevels'
    for i = 1:nlevels
        NumPos(i) = [results(i,:,condition)];
    end
    %Number of trials at each entry of 'StimLevels'
    OutOfNum = ones(1,nlevels)*ntrialseachcond;
    
    
    
    %Use the Logistic function
    PF = @PAL_Logistic;
    %@PAL_Logistic;  %Alternatives: PAL_Gumbel, PAL_Weibull,
    %PAL_Quick, PAL_logQuick,
    %PAL_CumulativeNormal, PAL_HyperbolicSecant
    
    %Threshold and Slope are free parameters, guess and lapse rate are fixed
    paramsFree = [1 1 0 0];  %1: free parameter, 0: fixed parameter
    
    %Parameter grid defining parameter space through which to perform a
    %brute-force search for values to be used as initial guesses in iterative
    %parameter search.
    searchGrid.alpha = 45:.01:53; %PSE
    searchGrid.beta = logspace(0,1,101); %slope
    searchGrid.gamma = 0.0;  %scalar here (since fixed) but may be vector %guess rate (lower asymptote)
    searchGrid.lambda = 0.02;  %ditto % lapse rate, finger error, upper asympt
    
    %Perform fit
    disp('Fitting function.....');
    [paramsValues LL exitflag] = PAL_PFML_Fit(StimLevels,NumPos, ...
        OutOfNum,searchGrid,paramsFree,PF);
    
    disp('done:')
    message = sprintf('Threshold estimate: %6.4f',paramsValues(1));
    disp(message);
    message = sprintf('Slope estimate: %6.4f\r',paramsValues(2));
    disp(message);
    
    %Create simple plot
    ProportionCorrectObserved=NumPos./OutOfNum;
    StimLevelsFineGrain=[min(StimLevels-0.05):max(StimLevels+0.05)./1000:max(StimLevels+0.05)];
    ProportionCorrectModel = PF(paramsValues,StimLevelsFineGrain);
    
    
    disp('Goodness of Fit')
    B = 1000;
    [Dev pDev DevSim converged] = PAL_PFML_GoodnessOfFit(StimLevels, NumPos, OutOfNum, paramsValues, paramsFree, B, PF,'searchGrid', searchGrid);
  
    disp(sprintf('Dev: %6.4f',Dev))
    disp(sprintf('pDev: %6.4f',pDev))
    disp(sprintf('N converged: %6.4f',sum(converged==1)))
    disp('--') %empty line
    
    
    plot(StimLevelsFineGrain,ProportionCorrectModel,'-','color',colorpoints(condition),'linewidth',2);
    plot(StimLevels,ProportionCorrectObserved,'LineStyle', 'None','Color', colorpoints(condition),'Marker',markershape(condition),'MarkerFaceColor', 'None','markersize',10);
    set(gca, 'fontsize',16);
    set(gca, 'Xtick',StimLevels);
    axis([min(StimLevels) max(StimLevels) 0 1]);
    xlabel('Stimulus Intensity');
    ylabel('P(Comparison More Pain)');
end

set(gca, 'fontsize',14);
set(gca, 'Xtick',StimLevels);
axis([min(StimLevels-0.05) max(StimLevels+0.05) 0 1]);
plot([0 5],[0.5 0.5])
plot([0.3 0.3], [0 1], 'LineStyle', '--')
if sessiontype == 1
    [leg] = legend('Thermal', '', 'Mechano', 'Location', 'Northwest');
else
    [leg] = legend('Left', '', 'Right', 'Location', 'Northwest');
end

%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%
%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%      For thermal and mechano by expectation %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

ntrialseachcond = 12*1;
% extract data


% Trial types

% Expectation / Pain type presented

% 1 {'ThermalHigh_thermal'} - 12 trials-pt
% 2 {'ThermalHigh_mechano'} - 6 trials-pt
% 3 {'MechanoHigh_mechano'} - 12 trials-pt
% 4 {'MechanoHigh_thermal'} - 6 trials-pt
% 5 {'Noexpect_thermal'} - 9 trials-pt
% 6 {'Noexpect_mechano'} - 9 trials-pt
% 


% lot thermal and mechano on separate figures
% 3 conditions each
% 
whichPainType = 2; % 1 thermal or 2 mechano

conditionorderthermal = [1, 4, 5];
conditionordermechano = [3, 2, 6];



%comparison_intensity_thermal = round([48.4580678851175, 49.144316797215, 49.8305657093124, 50.5168146214099, 51.2030635335074],1)

comparison_intensity_mechano =  [32, 64, 128, 256, 512]


%conditions_all_expects = nan(2,ntrialseachcond,5);



%conditions = nan(5,ntrialseachcond,5);
tmp = [];
results = nan(nlevels,1,3);
for condition = 1:3; %conditions od expectation
%     conditions(:,i) = find(subjectdata(:,1) == i); %find all intact trials, all BS trials...
%     tmp(:,i) = find(subjectdata(:,1) == i);
    for intensity = 1:nlevels %intensity
%       SFs(:,j) = find(subjectdata(:,2) == j);
%         conditions(j,:,i) = find(subjectdata(tmp(:,i),2) == j);
%         conditions(j,:,i) = find(subjectdata(tmp(:,i),2) == j);
%         tmp2(:,j) = find(subjectdata(:,2) == j);
%         subjectdata(tmp,tmp2)
        if whichPainType == 1 %thermal
            tmp = find( ... 
                 (data.TrialTypeID == conditionorderthermal(condition)) & ...
            data.ComparisonIntensity == comparison_intensity_thermal(intensity)  & ...
            data.SubRespComparisonMorePain == 1    ); % find condition 1, 4 or 5 where comparison intensity is the required one
            % and the response was 1, meaning comparison more pain
        else % mechano
            if sessiontype == 1
            
            
                tmp = find( ...
                 (data.TrialTypeID == conditionordermechano(condition)) & ...
                 data.ComparisonIntensity == comparison_intensity_mechano(intensity)  & ...
                 data.SubRespComparisonMorePain == 1    ); % find condition 2, 3 or 6 where comparison intensity is the required one
            else
                tmp = find( ...
                 (data.TrialTypeID == conditionordermechano(condition)) & ...
                 data.ComparisonIntensity == comparison_intensity_thermal(intensity)  & ...
                 data.SubRespComparisonMorePain == 1    ); % find condition 2, 3 or 6 where comparison intensity is the required one
            end
                % and the response was 1, meaning comparison more pain
        end
        
        
        
        
        %(:,2) == j) & (subjectdata(:,1) == i) & subjectdata(:,3) == 2)';
%         conditions(j,:,i) = tmp;
        results(intensity,1,condition) = size(tmp,1);

    end
end



%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%      For thermal and mechano by expectation %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% figure
figure; plot(1:nlevels, results(1:nlevels,1,1), 'ro-') %Thermal
hold on;
plot(1:nlevels, results(1:nlevels,1,2), 'bs-') % Mechano
plot(1:nlevels, results(1:nlevels,1,3), 'go-') %occl
%plot(1:5, results(1:5,1,4), 'kx-') %del sharp
%plot(1:5, results(1:5,1,5), 'cx-') %del fuzzy
axis([0.5 nlevels+0.5 -0.5 ntrialseachcond+0.5])
[leg] = legend('High', 'Low', 'None', 'Northwest');
ax = findobj(gcf,'type','axes'); %Retrieve the axes to be copied
hold off;

colorpoints(1) = 'r';
colorpoints(2) = 'b';
colorpoints(3) = 'g';
colorpoints(4) = 'k';
colorpoints(5) = 'c';

markershape(1) = 's';
markershape(2) = 's';
markershape(3) = 'o';
markershape(4) = 'x';
markershape(5) = 'x';



%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%      For thermal and mechano by expectation %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% palamedes analysis

multiplier = 2; % for multiple sessions, need to mult the n of trials

disp ('Palamedes...')
%Stimulus intensities
StimLevels = comparison_intensity_thermal; 
figure('name','Maximum Likelihood Psychometric Function Fitting');
    axes
    hold on

for condition = 1:3 %conditions
    
    
    switch condition
        case 1
            ntrialseachcond = 12*multiplier;
        case 2
            ntrialseachcond = 6*multiplier;
        case 3
            ntrialseachcond = 9*multiplier;
    end
    
    
    %Number of positive responses (e.g., 'yes' or 'correct' at each of the
    %   entries of 'StimLevels'
    for i = 1:nlevels
        NumPos(i) = [results(i,:,condition)];
    end
    %Number of trials at each entry of 'StimLevels'
    OutOfNum = ones(1,nlevels)*ntrialseachcond;
    
    
    %Use the Logistic function
    PF = @PAL_Logistic;
    %@PAL_Logistic;  %Alternatives: PAL_Gumbel, PAL_Weibull,
    %PAL_Quick, PAL_logQuick,
    %PAL_CumulativeNormal, PAL_HyperbolicSecant
    
    %Threshold and Slope are free parameters, guess and lapse rate are fixed
    paramsFree = [1 1 0 0];  %1: free parameter, 0: fixed parameter
    
    %Parameter grid defining parameter space through which to perform a
    %brute-force search for values to be used as initial guesses in iterative
    %parameter search.
    searchGrid.alpha = 45:.01:53; %PSE
    searchGrid.beta = logspace(0,1,101); %slope
    searchGrid.gamma = 0.02;  %scalar here (since fixed) but may be vector %guess rate (lower asymptote)
    searchGrid.lambda = 0.02;  %ditto % lapse rate, finger error, upper asympt
    
    %Perform fit
    disp('Fitting function.....');
    [paramsValues LL exitflag] = PAL_PFML_Fit(StimLevels,NumPos, ...
        OutOfNum,searchGrid,paramsFree,PF);
    
    disp('done:')
    message = sprintf('Threshold estimate: %6.4f',paramsValues(1));
    disp(message);
    message = sprintf('Slope estimate: %6.4f\r',paramsValues(2));
    disp(message);
    
    %Create simple plot
    ProportionCorrectObserved=NumPos./OutOfNum;
    StimLevelsFineGrain=[min(StimLevels-0.05):max(StimLevels+0.05)./1000:max(StimLevels+0.05)];
    ProportionCorrectModel = PF(paramsValues,StimLevelsFineGrain);
    
    
    disp('Goodness of Fit')
    B = 1000;
    [Dev pDev DevSim converged] = PAL_PFML_GoodnessOfFit(StimLevels, NumPos, OutOfNum, paramsValues, paramsFree, B, PF,'searchGrid', searchGrid);
  
    disp(sprintf('Dev: %6.4f',Dev))
    disp(sprintf('pDev: %6.4f',pDev))
    disp(sprintf('N converged: %6.4f',sum(converged==1)))
    disp('--') %empty line
    
    
    plot(StimLevelsFineGrain,ProportionCorrectModel,'-','color',colorpoints(condition),'linewidth',2);
    plot(StimLevels,ProportionCorrectObserved,'LineStyle', 'None','Color', colorpoints(condition),'Marker',markershape(condition),'MarkerFaceColor', 'None','markersize',10);
    set(gca, 'fontsize',16);
    set(gca, 'Xtick',StimLevels);
    axis([min(StimLevels) max(StimLevels) 0 1]);
    xlabel('Stimulus Intensity');
    ylabel('P(Comparison More Pain)');
end

set(gca, 'fontsize',14);
set(gca, 'Xtick',StimLevels);
axis([min(StimLevels-0.05) max(StimLevels+0.05) 0 1]);
plot([0 5],[0.5 0.5])
plot([0.3 0.3], [0 1], 'LineStyle', '--')
[leg] = legend('High', '', 'Low', '', 'None', 'Location', 'Northwest');